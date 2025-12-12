import os
import time
import requests
from urllib.parse import unquote, urlparse
from PIL import Image

OUTPUT_ROOT = "museum_images"
WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "MuseumImageDownloader/1.0 (contact: srane3094@gmail.com)"}

MAX_IMAGES_PER_MUSEUM = 11
MIN_WIDTH = 200
MIN_HEIGHT = 200
SLEEP = 0.2

CREATE_THUMBNAILS = True
THUMBNAIL_SIZE = (240, 160)

MANUAL_CATEGORIES = {
    # "Indian_Museum_Kolkata": [
    #     "Category:Indian Museum, Kolkata",
    #     "Category:Interior of the Indian Museum, Kolkata"
    # ],
    # "Victoria_Memorial_Kolkata": [
    #     "Category:Victoria Memorial, Kolkata",
    #     "Category:Victoria Memorial interior"
    # ],
    # "National_Museum_New_Delhi": [
    #     "Category:National Museum, New Delhi",
    #     "Category:Interior of the National Museum, New Delhi"
    # ],
    # "National_Gallery_of_Modern_Art_New_Delhi": [
    #     "Category:National Gallery of Modern Art, New Delhi",
    #     "Category:NGMA New Delhi"
    # ],
    # "Chhatrapati_Shivaji_Maharaj_Vastu_Sangrahalaya_Mumbai": [
    #     "Category:Chhatrapati Shivaji Maharaj Vastu Sangrahalaya",
    #     "Category:CSMVS Mumbai"
    # ],
    # "Salar_Jung_Museum_Hyderabad": [
    #     "Category:Salar Jung Museum",
    #     "Category:Collections of the Salar Jung Museum"
    # ],
    # "Government_Museum_Chennai": [
    #     "Category:Government Museum, Chennai"
    # ],
    # "National_Museum_of_Indian_Cinema_Mumbai": [
    #     "Category:National Museum of Indian Cinema"
    # ],
    # "Nehru_Science_Centre_Mumbai": [
    #     "Category:Nehru Science Centre"
    # ],
    # "Goa_Chitra_Museum_Benaulim": [
    #     "Category:Goa Chitra Museum"
    # ],
    # "Government_Museum_Bengaluru": [
    #     "Category:Government Museum, Bengaluru"
    # ],
    # "Government_Museum_Chennai_Art_History": [
    #     "Category:Government Museum, Chennai"
    # ],
    # "Albert_Hall_Museum_Jaipur": [
    #     "Category:Albert Hall Museum",
    #     "Category:Interior of the Albert Hall Museum"
    # ],
    # "Kerala_Museum_Ernakulam": [
    #     "Category:Kerala Museum"
    # ],
    # "Bihar_Museum_Patna": [
    #     "Category:Bihar Museum"
    # ],
    # "House_of_Jagat_Seth_Museum_Murshidabad": [
    #     "Category:House of Jagat Seth Museum"
    # ],
    # "Dr_MGR_Memorial_House_Chennai": [
    #     "Category:Dr. MGR Memorial House"
    # ],
    # "Godly_Museum_Mysore": [
    #     "Category:Godly Museum"
    # ],
    # "Vishwam_Museum_Mysore": [
    #     "Category:Vishwam Museum"
    # ],
    # "Regional_Museum_of_Natural_History_Mysore": [
    #     "Category:Regional Museum of Natural History, Mysuru"
    # ],
    # "Ram_Gauri_Sangrahalay_Gangtok": [
    #     "Category:Ram Gauri Sangrahalay"
    # ],
    # "Jehangir_Art_Gallery_Mumbai": [
    #     "Category:Jehangir Art Gallery"
    # ],
    # "Kiran_Nadar_Museum_of_Art_New_Delhi": [
    #     "Category:Kiran Nadar Museum of Art, New Delhi"
    # ],
    # "Kiran_Nadar_Museum_of_Art_Noida": [
    #     "Category:Kiran Nadar Museum of Art, Noida"
    # ],
    # "Triveni_Kala_Sangam_New_Delhi": [
    #     "Category:Triveni Kala Sangam"
    # ],
    # "Narrow_Gauge_Rail_Museum_Nagpur": [
    #     "Category:Narrow Gauge Rail Museum"
    # ],
    # "Central_Museum_Nagpur": [
    #     "Category:Central Museum, Nagpur"
    # ],
    # "Anthropological_Museum_Seminary_Hills_Nagpur": [
    #     "Category:Anthropological Museum, Nagpur"
    # ],
    # "Shantivan_Ambedkar_Museum_Nagpur": [
    #     "Category:Shantivan Ambedkar Museum"
    # ],
    # "Mysore_Picture_Gallery": [
    #     "Category:Mysore Picture Gallery"
    # ],
    # "Textile_Museum_Ahmedabad": [
    #     "Category:Textile Museum, Ahmedabad"
    # ],
    # "Toilet_Museum_New_Delhi": [
    #     "Category:Sulabh International Museum of Toilets"
    # ],
    # "House_of_Jagat_Seth_Museum_Murshidabad": [
    #     "Category:Jagat Seth House (Murshidabad)",  # 70+ files
    # ],

    # # Dr_MGR_Memorial_House_Chennai
    # # You used: "Category:Dr. MGR Memorial House"
    # "Dr_MGR_Memorial_House_Chennai": [
    #     "Category:MGR Memorial House",             # 4 files
    # ],

    # # Regional_Museum_of_Natural_History_Mysore
    # # You used: "Category:Regional Museum of Natural History, Mysuru"
    # "Regional_Museum_of_Natural_History_Mysore": [
    #     "Category:Regional Museum of Natural History, Mysore",  # 4 files
    # ],

    # # Government_Museum_Bengaluru (you only got 1)
    # # You used: "Category:Government Museum, Bengaluru"
    # "Government_Museum_Bengaluru": [
    #     "Category:Government Museum (Bangalore)",  # 150+ files
    # ],

    # # Narrow_Gauge_Rail_Museum_Nagpur
    # # You used: "Category:Narrow Gauge Rail Museum" (no such cat)
    # "Narrow_Gauge_Rail_Museum_Nagpur": [
    #     "Category:Railway museums in India",
    #     "Category:Visitor attractions in Nagpur",
    # ],

    # # Central_Museum_Nagpur – only 1 file on Commons, in a generic city cat
    # "Central_Museum_Nagpur": [
    #     "Category:Nagpur",
    # ],

    # # Textile_Museum_Ahmedabad – this is the Calico Museum of Textiles
    # "Textile_Museum_Ahmedabad": [
    #     "Category:Calico Museum of Textiles",
    # ],

    # # Toilet_Museum_New_Delhi – Sulabh International Museum of Toilets
    # "Toilet_Museum_New_Delhi": [
    #     "Category:Sulabh International",
    #     "Category:Public toilets in India",
    # ],

    # # Triveni Kala Sangam – only one image, lives in generic categories
    # "Triveni_Kala_Sangam_New_Delhi": [
    #     "Category:Art galleries in India",
    #     "Category:Buildings in New Delhi",
    # ],

    # # Kiran Nadar Museum of Art – there is no museum category,
    # # but there *are* images in the person category
    # "Kiran_Nadar_Museum_of_Art_New_Delhi": [
    #     "Category:Kiran Nadar",
    # ],
    # "Kiran_Nadar_Museum_of_Art_Noida": [
    #     "Category:Kiran Nadar",
    # ],

    # # Vishwam Museum Mysore – appears only on a commemorative stamp
    # "Vishwam_Museum_Mysore": [
    #     "Category:2018 stamps of India",
    #     "Category:My Stamp",
    # ],

    # # --- categories with subcategories (you got < 11, but more are available) ---

    # # CSMVS – you only got BISM.jpg because almost everything is in subcats
    # "Chhatrapati_Shivaji_Maharaj_Vastu_Sangrahalaya_Mumbai": [
    #     "Category:Chhatrapati Shivaji Maharaj Vastu Sangrahalaya",
    #     "Category:Exterior of Chhatrapati Shivaji Maharaj Vastu Sangrahalaya",
    #     "Category:Interior of Chhatrapati Shivaji Maharaj Vastu Sangrahalaya",
    #     "Category:Collections in the Chhatrapati Shivaji Maharaj Vastu Sangrahalaya",
    # ],

    # # NGMA New Delhi – you already have two good cats, add the higher-level ones
    # "National_Gallery_of_Modern_Art_New_Delhi": [
    #     "Category:National Gallery of Modern Art, India",
    #     "Category:Paintings in the National Gallery Of Modern Art, New Delhi",
    #     "Category:National Gallery of Modern Art, New Delhi",
    #     "Category:NGMA New Delhi",
    # ],
    #  "Museum_of_Everyday_Things_Delhi": [
    #     "Category:Museum of Everyday Things"
    # ],
    # "Bunker_Museum_Mumbai": [
    #     "Category:Bunker Museum Mumbai"
    # ],
    # "Nehru_Planetarium_Museum_New_Delhi": [
    #     "Category:Nehru Planetarium, New Delhi"
    # ],
    # "Jallianwala_Bagh_National_Memorial_Amritsar": [
    #     "Category:Jallianwala Bagh National Memorial"
    # ],
    # "Partition_Museum_Amritsar": [
    #     "Category:Partition Museum, Amritsar"
    # ],
    # "Punjab_State_War_Heroes_Memorial_Museum_Amritsar": [
    #     "Category:Punjab State War Heroes Memorial and Museum"
    # ],
    # "Jallianwala_Bagh_National_Memorial_Amritsar": [
    #     "Category:Jallianwala Bagh",
    #     "Category:Jallianwala Bagh National Memorial, Amritsar",
    #     "Category:Jallianwala Bagh massacre memorial",
    # ]

    # ------------------------------------------------------------------------
    # 2) Museum of Everyday Things — files exist under crafts/design, NOT museum tag
    #    No direct category — fallback to related parent/personal category
    # ------------------------------------------------------------------------
    # "Museum_of_Everyday_Things_Delhi": [
    #     "Category:Everyday objects in India",
    #     "Category:Design museums in India",
    #     "Category:Art and craft in India",
    #     "Category:Delhi",                 # fallback source, use filter later
    # ],

    # # ------------------------------------------------------------------------
    # # 3) Bunker Museum Mumbai — located inside Raj Bhavan, no official museum category
    # # ------------------------------------------------------------------------
    # "Bunker_Museum_Mumbai": [
    #     "Category:Raj Bhavan, Mumbai",
    #     "Category:Mumbai",
    #     "Category:Indian Army bunkers",
    # ],

    # # ------------------------------------------------------------------------
    # # 4) Punjab State War Heroes Memorial & Museum, Amritsar
    # #    Exists under different category format
    # # ------------------------------------------------------------------------
    # "Punjab_State_War_Heroes_Memorial_Museum_Amritsar": [
    #     "Category:Punjab State War Heroes Memorial & Museum",
    #     "Category:Punjab State War Heroes Memorial and Museum, Amritsar",
    #     "Category:War memorials in Punjab",
    #     "Category:Amritsar",
    # ]
    # "Nihal_Singh_Statue_and_Museum_Muktsar": [
    #     "Category:Nihal Singh Museum"
    # ]

    # …your existing entries…

    # Gandhi Smarak Sangrahalaya, Patna
    # Uses the general Bihar museums & Patna buildings categories;
    # this is where the file "Gandhi Sangralaya Patna.jpg" lives. :contentReference[oaicite:0]{index=0}
    # "Gandhi_Smarak_Sangrahalaya_Patna": [
    #     "Category:Museums in Bihar",
    #     "Category:Buildings in Patna",
    # ],

    # # Saptaparni Cave “museum” – the real Commons category is for the cave itself,
    # # named Sattapanni Cave. :contentReference[oaicite:1]{index=1}
    # "Saptaparni_Cave_Archeological_Museum_Bodh_Gaya": [
    #     "Category:Sattapanni Cave",
    #     "Category:Rajgir hills",
    # ],

    # # No actual Fukuoka Peace Museum in Patna on Commons – nothing to map to.
    # # Leave this empty so your script just logs 0 images and moves on.
    # "Fukuoka_Peace_Museum_Patna": [
    #     # no suitable Commons category or files found
    # ],

    # # Madhubani Art Museum – closest match is generic Madhubani art category. :contentReference[oaicite:2]{index=2}
    # "Madhubani_Art_Museum_Madhubani": [
    #     "Category:Art of Madhubani",
    # ]
    # "Tawang_War_Memorial_Museum": [
    #     "Category:Tawang War Memorial"
    # ],
#    "Ramnagar_Fort_Museum_Varanasi": [
#         "Category:Ramnagar Fort"
#     ],

#     # Ziro / Ziro Shai Heritage Museum — fallback to general Ziro valley images
#     "Ziro_Shai_Heritage_Museum": [
#         "Category:Ziro valley",
#         "Category:Ziro"   # maybe include a more general city-level category
#     ],

#     # Others — no reliable mapping found
#     "Donyi_Polo_Heritage_Museum_Itanagar": [],
#     "Hornbill_Festival_Ethnographic_Museum_Dimapur": [],
#     "State_Museum_Imphal": [],
#     "Gandhi_Museum_Varanasi": [],
#     "Nadesar_Palace_Museum_Varanasi": [],
   # Bharat Kala Bhavan — already works but limited images
#     "Bharat_Kala_Bhavan_Varanasi": [
#         "Category:Bharat Kala Bhavan",
#         "Category:Bharat Kala Bhavan, Banaras Hindu University",
#         "Category:Collections of Bharat Kala Bhavan",
#         "Category:Objects in Bharat Kala Bhavan",
#     ],

#     # Chhatrapati Shivaji Maharaj Maritime Museum, Mumbai
#     # No dedicated museum category, but images exist under maritime/naval categories
#     "Chhatrapati_Shivaji_Maharaj_Museum_of_Indian_Maritime_Heritage_Mumbai": [
#         "Category:Indian Navy",
#         "Category:Indian Maritime History",
#         "Category:Museum ships of India",
#     ],

#     # Kokandahalli Memorial & Museum, Mumbai — No media found
#     "Kokandahalli_Memorial_Museum_Mumbai": [],   # No commons category available

#     # Dr. Bhau Daji Lad Museum — exists, but under different names!
#     "Dr_Bhau_Daji_Lad_Museum_Mumbai": [
#         "Category:Dr. Bhau Daji Lad Museum",
#         "Category:Victoria and Albert Museum, Bombay",
#         "Category:Collections of Bhau Daji Lad Museum",
#         "Category:Interior of Dr. Bhau Daji Lad Museum",   # has images
#         "Category:Exterior of Dr. Bhau Daji Lad Museum",
#     ],

#     # Sion Fort Museum — museum doesn't exist separately; fort exists
#     "Sion_Fort_Museum_Mumbai": [
#         "Category:Sion Fort",   # plenty of fort images
#         "Category:Mumbai Forts",
#     ]
#   "Manav_Sangrahalaya_Museum_of_Man_Bhopal": [
#         "Category:Manav Sangrahalaya",
#         "Category:Manav Sangrahalaya, Bhopal"
#     ],
#     "Regional_Museum_of_Natural_History_Bhopal": [
#         "Category:Regional Museum of Natural History, Bhopal",
#         "Category:Regional Museum of Natural History"
#     ],
#     "Museum_of_Malwa_Culture_Indore": [
#         "Category:Museum of Malwa Culture",
#         "Category:Malwa Museum, Indore"
#     ],
#     "Rajwada_Museum_Indore": [
#         "Category:Rajwada Museum",
#         "Category:Rajwada, Indore"
#     ],
#     "State_Museum_Chennai": [
#         "Category:State Museum, Chennai",
#         "Category:Government Museum, Chennai"
#     ]
#  "Manav_Sangrahalaya_Museum_of_Man_Bhopal": [
#         "Category:Indira Gandhi Rashtriya Manav Sangrahalaya",
#         "Category:Museums in Bhopal",
#     ],

#     # Museum of Malwa Culture, Indore — no known Commons media
#     "Museum_of_Malwa_Culture_Indore": [],

#     # Rajwada Museum, Indore — fall back to palace/heritage Rajwada photos (if any)
#     "Rajwada_Museum_Indore": [
#         "Category:Rajwada",
#         "Category:Palaces in Madhya Pradesh",
#         "Category:Buildings and structures in Indore",
#     ]
#  "Connemara_Public_Library_and_Museum_Chennai": [
#         "Category:Connemara Public Library",
#         "Category:Connemara Public Library and Museum"
#     ],
#     "Museum_and_Art_Gallery_Chennai": [
#         "Category:Museum and Art Gallery, Chennai",
#         "Category:Government Museum, Chennai"
#     ],
#     "Fort_St_George_Museum_Chennai": [
#         "Category:Fort St. George, Chennai",
#         "Category:Fort St. George Museum"
#     ],
#     "Napier_Museum_Thiruvananthapuram": [
#         "Category:Napier Museum",
#         "Category:Napier Museum, Thiruvananthapuram"
#     ],
#     "Kerala_Folklore_Museum_Kochi": [
#         "Category:Kerala Folklore Museum",
#         "Category:Kerala Folklore Museum, Kochi"
#     ],
#     "Museum_of_Kerala_History_Muziris": [
#         "Category:Museum of Kerala History",
#         "Category:Museum of Kerala History, Muziris"
#     ],
#     "Kochi_Biennale_Foundation_Museum": [
#         "Category:Kochi Biennale Foundation",
#         "Category:Kochi Biennale Foundation Museum"
#     ],
#     "Sree_Chitra_Art_Gallery_Thiruvananthapuram": [
#         "Category:Sree Chitra Art Gallery",
#         "Category:Sree Chitra Art Gallery, Thiruvananthapuram"
#     ],
#     "Rajgir_Archaeological_Museum": [
#         "Category:Rajgir Archaeological Museum",
#         "Category:Rajgir Museum"
#     ],
#     "Zoological_Museum_Baripada": [
#         "Category:Zoological Museum, Baripada",
#         "Category:Zoological Museum Baripada"
#     ],
#     "Regional_Museum_of_Natural_History_Bhubaneswar": [
#         "Category:Regional Museum of Natural History, Bhubaneswar",
#         "Category:Regional Museum of Natural History, Odisha"
#     ],
#     "Odisha_State_Museum_Bhubaneswar": [
#         "Category:Odisha State Museum",
#         "Category:Odisha State Museum, Bhubaneswar"
#     ],
#     "Raghurajpur_Artist_Village_Museum_Puri": [
#         "Category:Raghurajpur Artist Village",
#         "Category:Raghurajpur Artist Village Museum"
#     ]
    #    "Raghurajpur_Artist_Village_Museum_Puri": [
    #     "Category:Raghurajpur",
    #     "Category:Pattachitra",
    #     "Category:Art of Odisha",
    # ],

    # # ------------------ 2) Kochi Biennale Foundation Museum --------------------
    # # No museum category — but Biennale categories have many artworks
    # "Kochi_Biennale_Foundation_Museum": [
    #     "Category:Kochi-Muziris Biennale",
    #     "Category:Art in Kochi",
    #     "Category:Contemporary art in India",
    # ],

    # # ------------------ 3) Sree Chitra Art Gallery, Thiruvananthapuram ----------
    # # Actual category exists under *different naming*
    # "Sree_Chitra_Art_Gallery_Thiruvananthapuram": [
    #     "Category:Sree Chitra Art Gallery",            # main
    #     "Category:Art museums and galleries in Kerala"
    # ],

    # # ------------------ 4) Rajgir Archaeological Museum ------------------------
    # # Very few/no images, fallback to region & archaeology
    # "Rajgir_Archaeological_Museum": [
    #     "Category:Rajgir",
    #     "Category:Archaeological museums in India",
    #     "Category:Museums in Bihar",
    # ],

    # # ------------------ 5) Zoological Museum, Baripada -------------------------
    # # No media found — leaving empty to skip
    # "Zoological_Museum_Baripada": [],

    # # ------------------ 6) Museum of Kerala History, Muziris -------------------
    # # Good fallback categories available
    # "Museum_of_Kerala_History_Muziris": [
    #     "Category:Museum of Kerala History",
    #     "Category:Kerala history",
    #     "Category:Museums in Kochi",
    # ],

    # # ------------------ 7) Fort St. George Museum, Chennai ---------------------
    # # Images exist under *Fort St George*, not museum name
    # "Fort_St_George_Museum_Chennai": [
    #     "Category:Fort St. George",
    #     "Category:Archaeological Survey of India museums",
    #     "Category:Museums in Chennai",
    # ]
    #  "Hirakud_Dam_Museum_Sambalpur": [
    #     "Category:Hirakud Dam Museum",
    #     "Category:Hirakud Dam Museum, Sambalpur"
    # ],
    # "Kalakshetra_Foundation_Museum_Chennai": [
    #     "Category:Kalakshetra Foundation",
    #     "Category:Kalakshetra Foundation Museum"
    # ],
    # "Museum_of_Evolutionary_Biology_Madras_University": [
    #     "Category:Museum of Evolutionary Biology",
    #     "Category:Museum of Evolutionary Biology, Madras University"
    # ],
    # "Coimbatore_Museum": [
    #     "Category:Coimbatore Museum",
    #     "Category:Coimbatore Government Museum"
    # ],
    # "Museum_of_Gems_and_Jewellery_Surat": [
    #     "Category:Museum of Gems & Jewellery, Surat",
    #     "Category:Gem and Jewellery Museum, Surat"
    # ],
    # "Vadodara_Museum_and_Picture_Gallery": [
    #     "Category:Vadodara Museum and Picture Gallery",
    #     "Category:Vadodara Museum & Picture Gallery"
    # ],
    # "Baroda_Museum_and_Picture_Gallery": [
    #     "Category:Baroda Museum & Picture Gallery",
    #     "Category:Vadodara Museum and Picture Gallery"
    # ],
    # "Science_City_Planetarium_Ahmedabad": [
    #     "Category:Science City, Ahmedabad",
    #     "Category:Science City Planetarium Museum"
    # ],
    # "Gandhi_Smrti_and_Darshan_Samiti_Museum_Ahmedabad": [
    #     "Category:Gandhi Smriti & Darshan Samiti",
    #     "Category:Gandhi Smriti & Darshan Samiti Museum"
    # ],
    # "Bombay_Dockyard_Museum_Mumbai": [
    #     "Category:Bombay Dockyard Museum",
    #     "Category:Bombay Dockyard Museum, Mumbai"
    # ],
    # "Air_Force_Museum_Hyderabad": [
    #     "Category:Air Force Museum, Hyderabad",
    #     "Category:Air Force Museum Hyderabad"
    # ],
    # "Birla_Industrial_and_Technological_Museum_Kolkata": [
    #     "Category:Birla Industrial & Technological Museum",
    #     "Category:BITM Kolkata"
    # ],
    # "Visva_Bharati_University_Museum_Shantiniketan": [
    #     "Category:Visva-Bharati University Museum",
    #     "Category:Visva-Bharati Museum, Shantiniketan"
    # ],
    # "Hans_Museum_Shantiniketan": [
    #     "Category:Hans Museum",
    #     "Category:Hans Museum, Shantiniketan"
    # ],
    # "Bishwa_Bangla_Gallery_Kolkata": [
    #     "Category:Bishwa Bangla Gallery",
    #     "Category:Bishwa Bangla Gallery, Kolkata"
    # ],
    # "Science_and_Technology_Museum_Kurukshetra": [
    #     "Category:Science and Technology Museum, Kurukshetra",
    #     "Category:Kurukshetra Science Museum"
    # ],
    # "Kurukshetra_Panorama_and_Science_Centre": [
    #     "Category:Kurukshetra Panorama and Science Centre",
    #     "Category:Kurukshetra Panorama & Science Centre"
    # ],
    # "Yadavindra_Gardens_and_Museum_Patiala": [
    #     "Category:Yadavindra Gardens",
    #     "Category:Yadavindra Gardens and Museum"
    # ],
    # "Maharana_Pratap_Memorial_Museum_Udaipur": [
    #     "Category:Maharana Pratap Memorial",
    #     "Category:Maharana Pratap Memorial Museum"
    # ],
    # "City_Palace_Museum_Udaipur": [
    #     "Category:City Palace, Udaipur",
    #     "Category:City Palace Museum, Udaipur"
    # ]
#         "Visva_Bharati_University_Museum_Shantiniketan": [
#         "Category:Visva-Bharati University",
#         "Category:Shantiniketan",
#         "Category:Art of Rabindranath Tagore",
#     ],

#     # No Hans Museum category found
#     "Hans_Museum_Shantiniketan": [],


#     # ---------------- Bishwa Bangla Gallery ------------------------
#     # Only brand/showroom promotional photos exist, no museum section
#     "Bishwa_Bangla_Gallery_Kolkata": [
#         "Category:Biswa Bangla",
#         "Category:Kolkata",   # generic fallback
#     ],


#     # ---------------- Kurukshetra Science Museums ------------------
#     # Main science centre works → 1 file downloaded already
#     "Kurukshetra_Panorama_and_Science_Centre": [
#         "Category:Kurukshetra Panorama and Science Centre",
#     ],

#     # No separate Science & Tech museum media
#     "Science_and_Technology_Museum_Kurukshetra": [],


#     # ---------------- Hirakud Dam Museum ---------------------------
#     # No museum media, only dam photos available
#     "Hirakud_Dam_Museum_Sambalpur": [
#         "Category:Hirakud Dam",
#     ],


#     # ---------------- Kalakshetra Foundation -----------------------
#     # Photos exist under Foundation, not Museum
#     "Kalakshetra_Foundation_Museum_Chennai": [
#         "Category:Kalakshetra Foundation",
#         "Category:Art of Tamil Nadu",
#     ],


#     # ---------------- Museum of Evolutionary Biology ----------------
#     "Museum_of_Evolutionary_Biology_Madras_University": [],


#     # ---------------- Coimbatore Museum ----------------------------
#     "Coimbatore_Museum": [
#         "Category:Coimbatore",
#         "Category:Natural history museums in India",
#     ],


#     # ---------------- Gems & Jewellery Surat -----------------------
#     "Museum_of_Gems_and_Jewellery_Surat": [],


#     # ---------------- Vadodara/Baroda Museum & Art Gallery ---------
#     # These two are SAME museum (Baroda = Vadodara)
#     "Vadodara_Museum_and_Picture_Gallery": [
#         "Category:Baroda Museum & Picture Gallery",
#         "Category:Vadodara Museum and Picture Gallery",
#     ],
#     "Baroda_Museum_and_Picture_Gallery": [
#         "Category:Baroda Museum & Picture Gallery",
#         "Category:Vadodara Museum and Picture Gallery",
#     ],


#     # ---------------- Ahmedabad Science City -----------------------
#     "Science_City_Planetarium_Ahmedabad": [
#         "Category:Science City, Ahmedabad",
#     ],


#     # ---------------- Gandhi Smriti & Darshan Samiti ---------------
#     # Images exist, but ONLY for **Delhi museum**, not Ahmedabad
#     "Gandhi_Smrti_and_Darshan_Samiti_Museum_Ahmedabad": [],


#     # ---------------- Dockyard Museum Mumbai -----------------------
#     "Bombay_Dockyard_Museum_Mumbai": [],


#     # ---------------- Air Force Museum Hyderabad -------------------
#     # No media uploaded under any name
#     "Air_Force_Museum_Hyderabad": [],
    # "Birla_Industrial_and_Technological_Museum_Kolkata": [
    #     "Category:Birla Industrial & Technological Museum",
    #     "Category:BITM Kolkata"
    # ],
    # "Visva_Bharati_University_Museum_Shantiniketan": [
    #     "Category:Visva-Bharati University Museum",
    #     "Category:Visva-Bharati Museum, Shantiniketan"
    # ],
    # "Hans_Museum_Shantiniketan": [
    #     "Category:Hans Museum",
    #     "Category:Hans Museum, Shantiniketan"
    # ],
    # "Bishwa_Bangla_Gallery_Kolkata": [
    #     "Category:Bishwa Bangla Gallery",
    #     "Category:Bishwa Bangla Gallery, Kolkata"
    # ],
    # "Science_and_Technology_Museum_Kurukshetra": [
    #     "Category:Science and Technology Museum, Kurukshetra",
    #     "Category:Kurukshetra Science Museum"
    # ],
    # "Kurukshetra_Panorama_and_Science_Centre": [
    #     "Category:Kurukshetra Panorama and Science Centre",
    #     "Category:Kurukshetra Panorama & Science Centre"
    # ],
    # "Yadavindra_Gardens_and_Museum_Patiala": [
    #     "Category:Yadavindra Gardens",
    #     "Category:Yadavindra Gardens and Museum"
    # ],
    # "Maharana_Pratap_Memorial_Museum_Udaipur": [
    #     "Category:Maharana Pratap Memorial",
    #     "Category:Maharana Pratap Memorial Museum"
    # ],
    # "City_Palace_Museum_Udaipur": [
    #     "Category:City Palace, Udaipur",
    #     "Category:City Palace Museum, Udaipur"
    # ],
    # "Rajasthan_State_Archives_Museum_Bikaner": [
    #     "Category:Rajasthan State Archives",
    #     "Category:Rajasthan State Archives Museum"
    # ],
    # "Johari_Bazaar_Heritage_Museum_Jaipur": [
    #     "Category:Johari Bazaar Heritage Museum",
    #     "Category:Johari Bazaar Museum"
    # ],
    # "Amber_Fort_Museum_Jaipur": [
    #     "Category:Amber Fort",
    #     "Category:Amber Fort Museum"
    # ],
    # "Jodhpur_Fort_Museum": [
    #     "Category:Jodhpur Fort",
    #     "Category:Jodhpur Fort Museum"
    # ],
    # "Umaid_Bhawan_Palace_Museum_Jodhpur": [
    #     "Category:Umaid Bhawan Palace Museum",
    #     "Category:Umaid Bhawan Palace, Jodhpur"
    # ],
    #  "MP_Govt_Tribal_Museum_Jabalpur": [
    #     "Category:MP Govt Tribal Museum",
    #     "Category:Tribal Museum, Jabalpur"
    # ],
    # "Chhattisgarh_State_Museum_Raipur": [
    #     "Category:Chhattisgarh State Museum",
    #     "Category:Chhattisgarh State Museum, Raipur"
    # ],
    # "Missionaries_of_Charity_Museum_Kolkata": [
    #     "Category:Missionaries of Charity Museum",
    #     "Category:Missionaries of Charity, Kolkata"
    # ],
    # "Museum_of_Traffic_Control_Mumbai": [
    #     "Category:Museum of Traffic Control",
    #     "Category:Traffic Control Museum, Mumbai"
    # ],
    # "Delhi_Quilt_Museum_New_Delhi": [
    #     "Category:Delhi Quilt Museum",
    #     "Category:Quilt Museum, Delhi"
    # ],
    # "National_Rail_Museum_New_Delhi": [
    #     "Category:National Rail Museum, New Delhi",
    #     "Category:National Rail Museum"
    # ],
    # "Rail_Heritage_Centre_Ahmedabad": [
    #     "Category:Rail Heritage Centre, Ahmedabad",
    #     "Category:Rail Heritage Centre"
    # ],
    # "Indian_Air_Force_Museum_Gwalior": [
    #     "Category:Indian Air Force Museum, Gwalior",
    #     "Category:Indian Air Force Museum"
    # ],
    # "All_India_Museum_of_Light_and_Sound_Chandigarh": [
    #     "Category:All India Museum of Light & Sound",
    #     "Category:Light and Sound Museum, Chandigarh"
    # ],
    # "Heritage_Transport_Museum_Gurgaon": [
    #     "Category:Heritage Transport Museum",
    #     "Category:Heritage Transport Museum, Gurugram"
    # ],
    # "Cyber_Museum_Hyderabad": [
    #     "Category:Cyber Museum",
    #     "Category:Cyber Museum, Hyderabad"
    # ],
    # "Regional_Maritime_Museum_Port_Blair": [
    #     "Category:Regional Maritime Museum, Port Blair",
    #     "Category:Port Blair Maritime Museum"
    # ],
    # "Cellular_Jail_Museum_Port_Blair": [
    #     "Category:Cellular Jail",
    #     "Category:Cellular Jail Museum, Port Blair"
    # ],
    # "Chandigarh_Architecture_Museum": [
    #     "Category:Chandigarh Architecture Museum",
    #     "Category:Architecture Museum, Chandigarh"
    # ],
    # "Museum_of_Christian_Art_Goa": [
    #     "Category:Museum of Christian Art",
    #     "Category:Christian Art Museum, Goa"
    # ],
    # "Ajanta_Ellora_Interpretation_Centre_Aurangabad": [
    #     "Category:Ajanta-Ellora Interpretation Centre",
    #     "Category:Ajanta Ellora Interpretation Centre, Aurangabad"
    # ],
    # "Bhadgaonstr_Museum_Bhangan": [
    #     "Category:Bhadgaonstr Museum",
    #     "Category:Bhadgaonst Museum"
    # ],
    # "Chitralekha_International_Art_Gallery_Guwahati": [
    #     "Category:Chitralekha International Art Gallery",
    #     "Category:Chitralekha Art Gallery, Guwahati"
    # ],
    # "Assam_State_Museum_Guwahati": [
    #     "Category:Assam State Museum",
    #     "Category:Assam State Museum, Guwahati"
    # ],
    # "Srimanta_Sankaradeva_Kalakshetra_Museum_Dispur": [
    #     "Category:Srimanta Sankaradeva Kalakshetra",
    #     "Category:Srimanta Sankaradeva Kalakshetra Museum"
    # ],
    # "Kangra_Fort_Museum_Kangra": [
    #     "Category:Kangra Fort",
    #     "Category:Kangra Fort Museum"
    # ],
    # "Himachal_State_Museum_Shimla": [
    #     "Category:Himachal State Museum",
    #     "Category:Himachal State Museum, Shimla"
    # ],
    # "Tibetan_Museum_McLeod_Ganj": [
    #     "Category:Tibetan Museum, McLeod Ganj",
    #     "Category:Tibetan Museum, Dharamshala"
    # ],
    # "Nalanda_Archaeological_Museum_Nalanda": [
    #     "Category:Nalanda Archaeological Museum",
    #     "Category:Nalanda Archaeological Museum, Nalanda"
    # ],
    # "West_Bengal_Film_Centre_Kolkata": [
    #     "Category:West Bengal Film Centre",
    #     "Category:West Bengal Film Centre, Kolkata"
    # ],
    # "Museum_of_Home_Plumbing_Mumbai": [
    #     "Category:Museum of Home Plumbing",
    #     "Category:Home Plumbing Museum, Mumbai"
    # ],
    # "Railway_Heritage_Centre_Chennai": [
    #     "Category:Railway Heritage Centre, Chennai",
    #     "Category:Railway Heritage Centre"
    # ],
    # "Tamil_Nadu_Archaeology_Museum_Chennai": [
    #     "Category:Tamil Nadu Archaeology Museum",
    #     "Category:Government Museum, Chennai"
    # ],
    # "Orissa_Tribal_and_Folk_Art_Museum_Bhubaneswar": [
    #     "Category:Orissa Tribal & Folk Art Museum",
    #     "Category:Tribal and Folk Art Museum, Bhubaneswar"
    # ],
    # "Jain_Museum_Humcha": [
    #     "Category:Jain Museum, Humcha",
    #     "Category:Humcha Jain Museum"
    # ],
    # "Government_Museum_Mysuru": [
    #     "Category:Government Museum, Mysuru",
    #     "Category:Government Museum Mysore"
    # ],
    # "Karnataka_Folk_Museum_Dandeli": [
    #     "Category:Karnataka Folk Museum",
    #     "Category:Karnataka Folk Museum, Dandeli"
    # ],
    # "Richmond_Town_Museum_Bengaluru": [
    #     "Category:Richmond Town Museum",
    #     "Category:Richmond Town Heritage Museum"
    # ],
    # "Mangalore_Port_Museum_Mangalore": [
    #     "Category:Mangalore Port Museum",
    #     "Category:Mangalore Port Museum, Mangalore"
    # ],
    # "Coastal_Art_Gallery_Mangaluru": [
    #     "Category:Coastal Art Gallery",
    #     "Category:Coastal Art Gallery, Mangaluru"
    # ],
    # "Pitalkhora_Museum_Yavatmal": [
    #     "Category:Pitalkhora Museum",
    #     "Category:Pitalkhora Archaeological Museum"
    # ],
    # "Eminence_Gallery_Hyderabad": [
    #     "Category:Eminence Gallery",
    #     "Category:Eminence Gallery, Hyderabad"
    # ],
    # "Salar_Jung_Museum_Annex_Hyderabad": [
    #     "Category:Salar Jung Museum Annex",
    #     "Category:Salar Jung Museum, Annex"
    # ],
    # "State_Archaeology_Museum_Hyderabad": [
    #     "Category:State Archaeology Museum, Hyderabad",
    #     "Category:State Archaeology Museum Hyderabad"
    # ],
    # "Hyderabad_Film_Metro_Museum": [
    #     "Category:Hyderabad Film Museum",
    #     "Category:Hyderabad Film Metro Museum"
    # ],
    # "AP_State_Museum_and_Zoo_Hyderabad": [
    #     "Category:AP State Museum & Zoo",
    #     "Category:Andhra Pradesh State Museum and Zoo"
    # ],
    # "Brihadeeswarar_Temple_Museum_Thanjavur": [
    #     "Category:Brihadeeswarar Temple Museum",
    #     "Category:Brihadeeswarar Temple Museum, Thanjavur"
    # ],
    # "Government_Museum_Kariavattam_Thiruvananthapuram": [
    #     "Category:Government Museum Kariavattam",
    #     "Category:Government Museum, Thiruvananthapuram"
    # ],
    # "Silent_Valley_Museum_Kollam": [
    #     "Category:Silent Valley Museum",
    #     "Category:Silent Valley Museum, Kollam"
    # ],
    # "Meenakshi_Temple_Museum_Thanjavur": [
    #     "Category:Meenakshi Temple Museum",
    #     "Category:Meenakshi Temple Museum, Thanjavur"
    # ],
    # "Nagaland_State_Museum_Kohima": [
    #     "Category:Nagaland State Museum",
    #     "Category:Nagaland State Museum, Kohima"
    # ],
    # "Tribal_Research_Centre_and_Museum_Aizawl": [
    #     "Category:Tribal Research Centre & Museum",
    #     "Category:Tribal Research Centre and Museum, Aizawl"
    # ],
    # "Chandra_Museum_Mandla": [
    #     "Category:Chandra Museum",
    #     "Category:Chandra Museum, Mandla"
    # ],
    # "Panna_Natural_History_Museum": [
    #     "Category:Panna Natural History Museum",
    #     "Category:Panna Natural History Museum, Madhya Pradesh"
    # ],
    # "Shilpgram_Cultural_Museum_Udaipur": [
    #     "Category:Shilpgram",
    #     "Category:Shilpgram Cultural Museum"
    # ],
    # "Rajasthan_Vintage_and_Classic_Car_Museum_Jaipur": [
    #     "Category:Rajasthan Vintage & Classic Car Museum",
    #     "Category:Vintage and Classic Car Museum, Jaipur"
    # ],
    # "Rajasthan_Vintage_and_Classic_Car_Museum_Jaipur": [
    #     "Category:Rajasthan Vintage & Classic Car Museum",
    #     "Category:Vintage and Classic Car Museum, Jaipur"
    # ],
    # "Shekhawati_Regional_Museum_Mandawa": [
    #     "Category:Shekhawati Regional Museum",
    #     "Category:Shekhawati Museum, Mandawa"
    # ],
    # "Fatehpur_Sikri_Museum": [
    #     "Category:Fatehpur Sikri Museum",
    #     "Category:Fatehpur Sikri Archaeological Museum"
    # ],
    # "Lucknow_State_Museum": [
    #     "Category:Lucknow State Museum",
    #     "Category:State Museum, Lucknow"
    # ],
    # "Bloom_Art_Gallery_Meerut": [
    #     "Category:Bloom Art Gallery",
    #     "Category:Bloom Art Gallery, Meerut"
    # ],
    # "Galib_Ki_Haveli_Museum_Old_Delhi": [
    #     "Category:Ghalib ki Haveli",
    #     "Category:Ghalib ki Haveli Museum"
    # ],
    # "Delhi_Art_Gallery_New_Delhi": [
    #     "Category:Delhi Art Gallery",
    #     "Category:DAG Delhi"
    # ],
    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi": [
    #     "Category:National Handicrafts & Handlooms Museum",
    #     "Category:Crafts Museum, Delhi"
    # ],
    # "National_Philatelic_Museum_New_Delhi": [
    #     "Category:National Philatelic Museum",
    #     "Category:National Philatelic Museum, New Delhi"
    # ],
    # "Nomadic_Textile_Museum_New_Delhi": [
    #     "Category:Nomadic Textile Museum",
    #     "Category:Nomadic Textile Museum, Delhi"
    # ]


# # -------------------------------- SHANTINIKETAN -------------------------------
#     "Visva_Bharati_University_Museum_Shantiniketan": [
#         "Category:Visva-Bharati University",
#         "Category:Shantiniketan"
#     ],
#     "Hans_Museum_Shantiniketan": [],

# # -------------------------------- KOLKATA ------------------------------------
#     "Bishwa_Bangla_Gallery_Kolkata": [
#         "Category:Biswa Bangla",
#         "Category:Kolkata"
#     ],
#     "Missionaries_of_Charity_Museum_Kolkata": [
#         "Category:Missionaries of Charity"
#     ],

# # -------------------------------- HARYANA / KURUKSHETRA ----------------------
#     "Science_and_Technology_Museum_Kurukshetra": [],
#     "Kurukshetra_Panorama_and_Science_Centre": [
#         "Category:Kurukshetra Panorama and Science Centre"
#     ],

# # -------------------------------- RAJASTHAN ----------------------------------
#     "Rajasthan_State_Archives_Museum_Bikaner": [
#         "Category:Rajasthan State Archives"
#     ],
#     "Johari_Bazaar_Heritage_Museum_Jaipur": [],
#     "Jodhpur_Fort_Museum": [
#         "Category:Jodhpur"
#     ],
#     "Umaid_Bhawan_Palace_Museum_Jodhpur": [
#         "Category:Umaid Bhawan Palace, Jodhpur"
#     ],
#     "Shilpgram_Cultural_Museum_Udaipur": [
#         "Category:Shilpgram"
#     ],
#     "Rajasthan_Vintage_and_Classic_Car_Museum_Jaipur": [],
#     "Shekhawati_Regional_Museum_Mandawa": [
#         "Category:Shekhawati"
#     ],
#     "Fatehpur_Sikri_Museum": [
#         "Category:Fatehpur Sikri"
#     ],
#     "Lucknow_State_Museum": [
#         "Category:State Museum, Lucknow"
#     ],
#     "Bloom_Art_Gallery_Meerut": [],

# # -------------------------------- MP / CHATTISGARH ---------------------------
#     "MP_Govt_Tribal_Museum_Jabalpur": [],
#     "Chhattisgarh_State_Museum_Raipur": [],
#     "Chandra_Museum_Mandla": [],
#     "Panna_Natural_History_Museum": [],

# # -------------------------------- WEST BENGAL -------------------------------
#     "Rail_Heritage_Centre_Ahmedabad": [],
#     "Delhi_Quilt_Museum_New_Delhi": [],
#     "Brihadeeswarar_Temple_Museum_Thanjavur": [
#         "Category:Brihadeeswarar Temple"
#     ],
#     "Meenakshi_Temple_Museum_Thanjavur": [
#         "Category:Meenakshi Temple"
#     ],

# # -------------------------------- TELANGANA / HYDERABAD ----------------------
#     "Cyber_Museum_Hyderabad": [],
#     "Regional_Maritime_Museum_Port_Blair": [],
#     "Eminence_Gallery_Hyderabad": [],
#     "Salar_Jung_Museum_Annex_Hyderabad": [
#         "Category:Salar Jung Museum"
#     ],
#     "State_Archaeology_Museum_Hyderabad": [],
#     "Hyderabad_Film_Metro_Museum": [],
#     "AP_State_Museum_and_Zoo_Hyderabad": [],

# # -------------------------------- KARNATAKA ----------------------------------
#     "Government_Museum_Mysuru": [],
#     "Karnataka_Folk_Museum_Dandeli": [],
#     "Richmond_Town_Museum_Bengaluru": [],
#     "Mangalore_Port_Museum_Mangalore": [],
#     "Coastal_Art_Gallery_Mangaluru": [],
#     "Jain_Museum_Humcha": [
#         "Category:Humcha Jain Temple"
#     ],

# # -------------------------------- ORISSA -------------------------------------
#     "Silent_Valley_Museum_Kollam": [],
#     "Orissa_Tribal_and_Folk_Art_Museum_Bhubaneswar": [],

# # -------------------------------- NEW DELHI ----------------------------------
#     "Delhi_Art_Gallery_New_Delhi": [
#         "Category:DAG (Delhi Art Gallery)"
#     ],
#     "National_Handicrafts_and_Handlooms_Museum_New_Delhi": [
#         "Category:Crafts Museum, Delhi"
#     ],
#     "National_Philatelic_Museum_New_Delhi": [
#         "Category:Indian postage stamps"  # no museum photos, only stamps exist
#     ],
#     "Nomadic_Textile_Museum_New_Delhi": [],

# # -------------------------------- OTHERS -------------------------------------
#     "Science_City_Planetarium_Ahmedabad": [
#         "Category:Science City, Ahmedabad"
#     ],
#     "Indian_Air_Force_Museum_Gwalior": [],  # Delhi has museum, Gwalior doesn't
#     "All_India_Museum_of_Light_and_Sound_Chandigarh": [],
#     "Heritage_Transport_Museum_Gurgaon": [], # Private photos exist outside Wikimedia
#     "Bombay_Dockyard_Museum_Mumbai": [],
    # "Rail_Coach_Factory_Heritage_Museum_Rae_Bareli": [
    #     "Category:Rail Coach Factory Heritage Museum",
    #     "Category:RCF Heritage Museum Rae Bareli"
    # ],
    # "Museum_of_Mahjong_Hyderabad": [
    #     "Category:Mahjong Museum",
    #     "Category:Museum of Mahjong"
    # ],
    # "Punjab_Heritage_Museum_Ludhiana": [
    #     "Category:Punjab Heritage Museum",
    #     "Category:Punjab Heritage Museum, Ludhiana"
    # ],
    # "Berhampur_Archaeological_Museum": [
    #     "Category:Berhampur Archaeological Museum",
    #     "Category:Berhampur Museum"
    # ],
    # "Museum_of_Sacred_Arts_Puspakamal_Guwahati": [
    #     "Category:Sacred Arts Museum",
    #     "Category:Museum of Sacred Arts Guwahati"
    # ],
    # "Ancient_Monuments_Museum_Patan": [
    #     "Category:Ancient Monuments Museum",
    #     "Category:Ancient Monuments Museum, Patan"
    # ],
    # "Rizvi_College_Art_Gallery_Mumbai": [
    #     "Category:Rizvi College Art Gallery",
    #     "Category:Rizvi Art Gallery Mumbai"
    # ],
    # "Museum_of_Rural_Life_and_Crafts_Jhajjar": [
    #     "Category:Museum of Rural Life & Crafts",
    #     "Category:Rural Life and Crafts Museum Jhajjar"
    # ],
    # "Haryana_State_Museum_Kurukshetra": [
    #     "Category:Haryana State Museum",
    #     "Category:Haryana State Museum Kurukshetra"
    # ],
    # "Gufa_Art_Museum_Bhopal": [
    #     "Category:Gufa Art Museum",
    #     "Category:Gufa Art Gallery Bhopal"
    # ],
    # "Indira_Gandhi_Memorial_Museum_Srinagar": [
    #     "Category:Indira Gandhi Memorial Museum",
    #     "Category:Indira Gandhi Museum Srinagar"
    # ],
    # "Dogra_Art_Museum_Srinagar": [
    #     "Category:Dogra Art Museum",
    #     "Category:Dogra Art Gallery Srinagar"
    # ],
    # "Mahatma_Gandhi_Memorial_Museum_Rajkot": [
    #     "Category:Mahatma Gandhi Memorial Museum",
    #     "Category:Gandhi Memorial Museum Rajkot"
    # ],
    # "Gandhi_Memorial_Gandhinagar": [
    #     "Category:Gandhi Memorial",
    #     "Category:Gandhi Memorial Gandhinagar"
    # ],
    # "State_Bank_Museum_Mumbai": [
    #     "Category:State Bank Museum",
    #     "Category:SBI Museum Mumbai"
    # ],
    # "Bank_Note_Museum_Mumbai": [
    #     "Category:Bank Note Museum",
    #     "Category:Bank Note Museum Mumbai"
    # ],
    # "World_Buddhism_Museum_Hyderabad": [
    #     "Category:World Buddhism Museum",
    #     "Category:Buddhism Museum Hyderabad"
    # ],
    # "Museum_of_Buddhist_Art_Bodh_Gaya": [
    #     "Category: Museum of Buddhist Art",
    #     "Category:Buddhist Art Museum Bodh Gaya"
    # ],
    # "Glass_Museum_Hyderabad": [
    #     "Category:Glass Museum Hyderabad",
    #     "Category:Glass Art Museum Hyderabad"
    # ],
    # "Paradise_Art_Gallery_Patna": [
    #     "Category:Paradise Art Gallery",
    #     "Category:Paradise Art Gallery Patna"
    # ],
    # "Museum_Malabar_Guruvayur": [
    #     "Category:Malabar Museum",
    #     "Category:Museum Malabar Guruvayur"
    # ],
    # "Kerala_Spices_Museum_Kozhikode": [
    #     "Category:Kerala Spices Museum",
    #     "Category:Spice Museum Kozhikode"
    # ],
    # "City_Museum_Vadodara": [
    #     "Category:City Museum Vadodara",
    #     "Category:Vadodara City Museum"
    # ],
    # "Chacha_Nehru_Bal_Chikitsalaya_Museum_Surat": [
    #     "Category:CNC Museum Surat",
    #     "Category:Chacha Nehru Bal Chikitsalaya Museum"
    # ],
    # "Maritime_Archaeology_Museum_Kochi": [
    #     "Category:Maritime Archaeology Museum",
    #     "Category:Maritime Museum Kochi"
    # ],
    # "Tibetan_Handicraft_Museum_McLeod_Ganj": [
    #     "Category:Tibetan Handicraft Museum",
    #     "Category:Tibetan Handicraft Museum McLeod Ganj"
    # ],
    # "Kargil_War_Memorial_Museum_Dras": [
    #     "Category:Kargil War Memorial",
    #     "Category:Kargil War Memorial Museum"
    # ],
    # "Hall_of_Fame_Museum_Chamba": [
    #     "Category:Hall of Fame Museum Chamba",
    #     "Category:Hall of Fame Chamba"
    # ],
    # "Zanskar_Heritage_Museum_Padum": [
    #     "Category:Zanskar Heritage Museum",
    #     "Category:Padum Heritage Museum"
    # ],
    # "Art_and_Photo_Gallery_Shillong": [
    #     "Category:Art & Photo Gallery Shillong",
    #     "Category:Art Gallery Shillong"
    # ],
    # "Khasi_Heritage_Museum_Shillong": [
    #     "Category:Khasi Heritage Museum",
    #     "Category:Khasi Museum Shillong"
    # ],
    # "Nagaland_State_Art_and_Culture_Museum_Kohima": [
    #     "Category:Nagaland State Art & Culture Museum",
    #     "Category:Art and Culture Museum Kohima"
    # ],
    # "Tikob_Heritage_Museum_Dimapur": [
    #     "Category:Tikob Heritage Museum",
    #     "Category:Tikob Museum Dimapur"
    # ],
    # "Caribbean_Heritage_India_Exhibit_Chennai": [
    #     "Category:Caribbean Heritage Museum India Exhibit",
    #     "Category:Caribbean or Guyana Heritage Gallery Chennai"
    # ],
    # "Rail_and_Steam_Heritage_Museum_Nagpur": [
    #     "Category:Rail & Steam Heritage Museum",
    #     "Category:Rail and Steam Museum Nagpur"
    # ],
    # "Museum_of_Evolutionary_Science_Pune": [
    #     "Category:Museum of Evolutionary Science",
    #     "Category:Evolutionary Science Museum Pune"
    # ],
    # "Patiala_Heritage_Gallery": [
    #     "Category:Patiala Heritage Gallery",
    #     "Category:Patiala Heritage Museum"
    # ],
    # "Fatehgarh_Sahib_Heritage_Museum": [
    #     "Category:Fatehgarh Sahib Heritage Museum",
    #     "Category:Fatehgarh Sahib Museum"
    # ],
    # "Maharaja_Ranjit_Singh_Museum_Ludhiana": [
    #     "Category:Maharaja Ranjit Singh Museum",
    #     "Category:Ranjit Singh Museum Ludhiana"
    # ],
    # "Museum_of_Kashmir_Arts_Srinagar": [
    #     "Category:Museum of Kashmir Arts",
    #     "Category:Kashmir Arts Museum Srinagar"
    # ],
    #  "Balipara_Foundation_Nature_Museum_Assam": [
    #     "Category:Balipara Foundation",
    #     "Category:Nature Museum Balipara"
    # ],
    # "Diptanshu_Art_Centre_and_Museum_Varanasi": [
    #     "Category:Diptanshu Art Centre",
    #     "Category:Diptanshu Art Museum Varanasi"
    # ],
    # "Lok_Kala_Sanskriti_Sangrahalaya_Gwalior": [
    #     "Category:Lok Kala Sanskriti Sangrahalaya",
    #     "Category:Cultural Museum Gwalior"
    # ],
    # "Museum_of_Gods_Own_Country_Thiruvananthapuram": [
    #     "Category:Museum of God's Own Country",
    #     "Category:Travancore Royal Family Museum"
    # ],
    # "Museum_of_the_North_East_Hills_Mokokchung": [
    #     "Category:Museum of the North-East Hills",
    #     "Category:NE Hills Museum Mokokchung"
    # ],
    # "Ladakh_Folklore_Museum_Leh": [
    #     "Category:Ladakh Folklore Museum",
    #     "Category:Folklore Museum Leh"
    # ],
    # "Changthang_Wildlife_Sanctuary_Interpretation_Centre_Ladakh": [
    #     "Category:Changthang Wildlife Sanctuary",
    #     "Category:Changthang Interpretation Centre"
    # ],
    # "Lepcha_Heritage_Museum_Gangtok": [
    #     "Category:Lepcha Heritage Museum",
    #     "Category:Lepcha Museum Gangtok"
    # ],
    # "IHBT_Museum_Solan": [
    #     "Category:Institute of Himalayan Bioresource Technology Museum",
    #     "Category:IHBT Museum Solan"
    # ],
    # "Science_and_Technology_Museum_Raipur": [
    #     "Category:Science & Technology Museum Raipur",
    #     "Category:Science Museum Raipur"
    # ],
    # "Jawaharlal_Nehru_Museum_and_Art_Gallery_Nagaland": [
    #     "Category:Jawaharlal Nehru Museum & Art Gallery",
    #     "Category:Nehru Art Gallery Nagaland"
    # ],
    # "Bihar_Museum_Annex_Patna": [
    #     "Category:Bihar Museum Annex",
    #     "Category:Museum Annex Patna"
    # ],
    # "Modern_Art_Gallery_Thiruvananthapuram": [
    #     "Category:Modern Art Gallery Thiruvananthapuram",
    #     "Category:Modern Art Museum Kerala"
    # ],
    # "Sangai_Deer_Interpretation_Centre_Manipur": [
    #     "Category:Sangai Deer Interpretation Centre",
    #     "Category:Keibul Lamjao Interpretation Centre"
    # ],
    # "Assam_State_Museum_Guwahati_2": [
    #     "Category:Assam State Museum",
    #     "Category:Assam State Museum Guwahati"
    # ],
    # "District_Museum_Dhubri": [
    #     "Category:District Museum Dhubri",
    #     "Category:District Museum Assam"
    # ],
    # "Nilima_Barua_Folk_Art_Museum_Gauripur": [
    #     "Category:Nilima Barua Folk Art Museum",
    #     "Category:Folk Art Museum Gauripur"
    # ],
    # "District_Museum_Barpeta": [
    #     "Category:District Museum Barpeta",
    #     "Category:Barpeta Museum"
    # ],
    # "District_Museum_Mangaldai": [
    #     "Category:District Museum Mangaldai",
    #     "Category:Mangaldai Museum"
    # ],
    # "District_Museum_Tezpur": [
    #     "Category:District Museum Tezpur",
    #     "Category:Tezpur Museum"
    # ],
    # "District_Museum_Nagaon": [
    #     "Category:District Museum Nagaon",
    #     "Category:Nagaon Museum"
    # ],
    # "Lokopriya_Gopinath_Bordoloi_Memorial_Museum_Raha": [
    #     "Category:Lokopriya Gopinath Bordoloi Memorial Museum",
    #     "Category:Gopinath Bordoloi Museum Raha"
    # ],
    # "Srimanta_Sankardev_Kalakshetra_Museum_Dispur_2": [
    #     "Category:Srimanta Sankardev Kalakshetra",
    #     "Category:Kalakshetra Museum Assam"
    # ],
    # "Science_Museum_Khanapara": [
    #     "Category:Science Museum Khanapara",
    #     "Category:Regional Science Museum Khanapara"
    # ],
    # "Guwahati_Planetarium": [
    #     "Category:Guwahati Planetarium",
    #     "Category:Planetarium Guwahati"
    # ],
    # "Regional_Science_Museum_Khanapara": [
    #     "Category:Regional Science Museum Assam",
    #     "Category:Khanapara Science Centre"
    # ],
    # "Margherita_Coal_Heritage_Museum": [
    #     "Category:Margherita Coal Heritage Museum",
    #     "Category:Coal Museum Margherita"
    # ],
    # "Don_Bosco_Centre_for_Indigenous_Cultures": [
    #     "Category:Don Bosco Centre for Indigenous Cultures",
    #     "Category:Don Bosco Museum Shillong"
    # ],
    # "Rhino_Heritage_Museum_Shillong": [
    #     "Category:Rhino Heritage Museum",
    #     "Category:Assam Rifles Rhino Museum"
    # ],
    # "Air_Force_Museum_Shillong": [
    #     "Category:Air Force Museum Shillong",
    #     "Category:Air Force Museum Meghalaya"
    # ],
    # "Capt_Williamson_Sangma_State_Museum_Shillong": [
    #     "Category:Capt. Williamson Sangma Museum",
    #     "Category:State Museum Shillong"
    # ],
    # "Wankhar_Entomology_Museum_Shillong": [
    #     "Category:Wankhar Entomology Museum",
    #     "Category:Butterfly Museum Shillong"
    # ],
    # "Manekshaw_Museum_Shillong": [
    #     "Category:Manekshaw Museum Shillong",
    #     "Category:Indian Army Museum Shillong"
    # ],
    # "Geological_Museum_Shillong": [
    #     "Category:Geological Museum Shillong",
    #     "Category:Geology Museum Meghalaya"
    # ],
    # "Mizoram_State_Museum_Aizawl": [
    #     "Category:Mizoram State Museum",
    #     "Category:State Museum Aizawl"
    #    "CIBS_Museum_Leh": [
    #     "Category:Central Institute of Buddhist Studies Museum",
    #     "Category:CIBS Museum Leh"
    # ],
    # "Munshi_Aziz_Bhat_Museum_Kargil": [
    #     "Category:Munshi Aziz Bhat Museum",
    #     "Category:Kargil Trade Museum"
    # ],
    # "Hall_of_Fame_Museum_Leh": [
    #     "Category:Hall of Fame Leh",
    #     "Category:Hall of Fame Museum Ladakh"
    # ],
    # "Stok_Palace_Museum_Ladakh": [
    #     "Category:Stok Palace Museum",
    #     "Category:Stok Palace Ladakh"
    # ],
    # "Zorawar_Fort_Museum_Leh": [
    #     "Category:Zorawar Fort",
    #     "Category:Zorawar Fort Museum Leh"
    # ],
    # "Leh_Palace_Museum": [
    #     "Category:Leh Palace",
    #     "Category:Leh Palace Museum"
    # ],
    # "Alchi_Monastery_Museum": [
    #     "Category:Alchi Monastery",
    #     "Category:Alchi Museum"
    # ],
    # "Tsemo_Monastery_Museum_Leh": [
    #     "Category:Tsemo Monastery",
    #     "Category:Tsemo Museum Leh"
    # ],
    # "Hemis_Museum_Ladakh": [
    #     "Category:Hemis Monastery",
    #     "Category:Hemis Museum"
    # ],
    # "Likir_Monastery_Museum": [
    #     "Category:Likir Monastery",
    #     "Category:Likir Museum"
    # ],
    # "Thiksey_Monastery_Museum": [
    #     "Category:Thiksey Monastery",
    #     "Category:Thiksey Museum"
    # ],
    # "Lamayuru_Monastery_Museum": [
    #     "Category:Lamayuru Monastery",
    #     "Category:Lamayuru Museum"
    # ],
    # "Phugtal_Monastery_Museum": [
    #     "Category:Phugtal Monastery",
    #     "Category:Phugtal Museum"
    # ],
    # "Assam_Institute_of_Research_Ethnological_Museum": [
    #     "Category:Assam Institute of Research",
    #     "Category:Ethnological Museum Assam"
    # ],
    # "Anthropological_Museum_Imphal": [
    #     "Category:Anthropological Museum Imphal",
    #     "Category:Manipur Anthropological Museum"
    # ],
    # "Meghalaya_State_Museum_Shillong": [
    #     "Category:Meghalaya State Museum",
    #     "Category:Meghalaya State Museum, Shillong"
    # ],
    # "Tribal_Research_Institute_Museum_Mawlai": [
    #     "Category:Tribal Research Institute Museum",
    #     "Category:Tribal Research Institute, Mawlai"
    # ],
    # "Science_and_Technology_Museum_Raipur_2": [
    #     "Category:Science & Technology Museum, Raipur",
    #     "Category:Science and Technology Museum Raipur"
    # ],
    # "District_Museum_Berhampur": [
    #     "Category:District Museum, Berhampur",
    #     "Category:Berhampur District Museum"
    # ],
    # "Zoological_Museum_Baripada": [
    #     "Category:Zoological Museum, Baripada",
    #     "Category:Baripada Zoological Museum"
    # ],
    # "Odisha_Tribal_and_Folk_Art_Museum_Bhubaneswar_2": [
    #     "Category:Orissa Tribal & Folk Art Museum",
    #     "Category:Odisha Tribal and Folk Art Museum"
    # ],
    # "Ancient_Monuments_Museum_Patan_2": [
    #     "Category:Ancient Monuments Museum, Patan",
    #     "Category:Patan Ancient Monuments Museum"
    # ],
    # "Museum_of_Gems_and_Jewellery_Surat_2": [
    #     "Category:Museum of Gems & Jewellery, Surat",
    #     "Category:Gems and Jewellery Museum Surat"
    # ],
    # "Bank_Note_Museum_Mumbai_2": [
    #     "Category:Bank Note Museum",
    #     "Category:Bank Note Museum, Mumbai"
    # ],
    # "State_Bank_Museum_Mumbai_2": [
    #     "Category:State Bank Museum",
    #     "Category:State Bank Museum, Mumbai"
    # ],
    # "Museum_of_Home_Plumbing_Mumbai_2": [
    #     "Category:Museum of Home Plumbing",
    #     "Category:Home Plumbing Museum, Mumbai"
    # ],
    # "Museum_of_Traffic_Control_Mumbai_2": [
    #     "Category:Museum of Traffic Control",
    #     "Category:Traffic Control Museum, Mumbai"
    # ],
    # "Mangalore_Port_Museum_Mangalore_2": [
    #     "Category:Mangalore Port Museum",
    #     "Category:Mangalore Port Museum, Mangalore"
    # ],
    # "Richmond_Town_Museum_Bengaluru_2": [
    #     "Category:Richmond Town Museum",
    #     "Category:Richmond Town Museum, Bengaluru"
    # ],
    # "Government_Museum_Mysuru_2": [
    #     "Category:Government Museum, Mysuru",
    #     "Category:Government Museum Mysore"
    # ],
    # "Karnataka_Folk_Museum_Dandeli_2": [
    #     "Category:Karnataka Folk Museum",
    #     "Category:Karnataka Folk Museum, Dandeli"
    # ],
    # "Jain_Museum_Humcha_2": [
    #     "Category:Jain Museum, Humcha",
    #     "Category:Humcha Jain Museum"
    # ],
    # "Pitalkhora_Museum_Yavatmal_2": [
    #     "Category:Pitalkhora Museum",
    #     "Category:Pitalkhora Archaeological Museum"
    # ],
    # "Museum_of_Mahjong_Hyderabad_2": [
    #     "Category:Mahjong Museum",
    #     "Category:Museum of Mahjong, Hyderabad"
    # ],
    # "Eminence_Gallery_Hyderabad_2": [
    #     "Category:Eminence Gallery",
    #     "Category:Eminence Gallery, Hyderabad"
    # ],
    # "State_Archaeology_Museum_Hyderabad_2": [
    #     "Category:State Archaeology Museum, Hyderabad",
    #     "Category:State Archaeology Museum Hyderabad"
    # ],
    # "Hyderabad_Film_Metro_Museum_2": [
    #     "Category:Hyderabad Film Museum",
    #     "Category:Hyderabad Film Metro Museum"
    # ],
    # "AP_State_Museum_and_Zoo_Hyderabad_2": [
    #     "Category:AP State Museum & Zoo",
    #     "Category:Andhra Pradesh State Museum and Zoo"
    # ],
    # "Regional_Museum_of_Natural_History_Bhopal_2": [
    #     "Category:Regional Museum of Natural History, Bhopal",
    #     "Category:Regional Museum of Natural History Bhopal"
    # ],
    # "Gufa_Art_Museum_Bhopal_2": [
    #     "Category:Gufa Art Museum",
    #     "Category:Gufa Art Gallery Bhopal"
    # ],
    # "Chandra_Museum_Mandla_2": [
    #     "Category:Chandra Museum",
    #     "Category:Chandra Museum, Mandla"
    # ],
    # "Panna_Natural_History_Museum_2": [
    #     "Category:Panna Natural History Museum",
    #     "Category:Panna Natural History Museum, Madhya Pradesh"
    # ],
    # "Lok_Kala_Sanskriti_Sangrahalaya_Gwalior_2": [
    #     "Category:Lok Kala Sanskriti Sangrahalaya",
    #     "Category:Lok Kala Museum Gwalior"
    # ],
    # "Museum_of_Rural_Life_and_Crafts_Jhajjar_2": [
    #     "Category:Museum of Rural Life & Crafts",
    #     "Category:Rural Life and Crafts Museum Jhajjar"
    # ],
    # "Haryana_State_Museum_Kurukshetra_2": [
    #     "Category:Haryana State Museum",
    #     "Category:Haryana State Museum, Kurukshetra"
    # ],
    # "Heritage_Transport_Museum_Gurgaon_2": [
    #     "Category:Heritage Transport Museum",
    #     "Category:Heritage Transport Museum, Gurugram"
    # ],
    # "Science_and_Technology_Museum_Kurukshetra_2": [
    #     "Category:Science and Technology Museum, Kurukshetra",
    #     "Category:Kurukshetra Science Museum"
    # ],
    # "Air_Force_Museum_Hyderabad_2": [
    #     "Category:Air Force Museum, Hyderabad",
    #     "Category:Air Force Museum Hyderabad"
    # ],
    # "Bombay_Dockyard_Museum_Mumbai_2": [
    #     "Category:Bombay Dockyard Museum",
    #     "Category:Bombay Dockyard Museum, Mumbai"
    # ],
    # "Nehru_Planetarium_Museum_New_Delhi_2": [
    #     "Category:Nehru Planetarium, New Delhi",
    #     "Category:Nehru Planetarium Delhi"
    # ]
    #  "CIBS_Museum_Leh": [
    #     "Category:Central Institute of Buddhist Studies",
    #     "Category:Buddhism in Ladakh",
    #     "Category:Leh"
    # ],
    # "Munshi_Aziz_Bhat_Museum_Kargil": [
    #     "Category:Munshi Aziz Bhat Museum",
    #     "Category:Kargil"
    # ],
    # "Hall_of_Fame_Museum_Leh": [
    #     "Category:Hall of Fame Leh",
    #     "Category:Indian Army in Ladakh",
    #     "Category:Leh"
    # ],
    # "Stok_Palace_Museum_Ladakh": [
    #     "Category:Stok Palace",
    #     "Category:Royal Family of Ladakh",
    #     "Category:Leh"
    # ],
    # "Zorawar_Fort_Museum_Leh": [
    #     "Category:Zorawar Fort",
    #     "Category:Leh Forts",
    #     "Category:Leh"
    # ],
    # "Tsemo_Monastery_Museum_Leh": [
    #     "Category:Tsemo Monastery",
    #     "Category:Leh Monuments",
    #     "Category:Leh"
    # ],
    # "Phugtal_Monastery_Museum": [
    #     "Category:Phugtal Monastery",
    #     "Category:Zanskar",
    #     "Category:Buddhist Monasteries in Ladakh"
    # ],
    # "Assam_Institute_of_Research_Ethnological_Museum": [
    #     "Category:Anthropology of Assam",
    #     "Category:Ethnology of India",
    #     "Category:Assam Culture"
    # ],
    # "Anthropological_Museum_Imphal": [
    #     "Category:Imphal",
    #     "Category:Culture of Manipur",
    #     "Category:Anthropology in India"
    # ],
    # "Meghalaya_State_Museum_Shillong": [
    #     "Category:Shillong",
    #     "Category:Culture of Meghalaya",
    #     "Category:Museums in Meghalaya"
    # ],
    # "Tribal_Research_Institute_Museum_Mawlai": [
    #     "Category:Mawlai",
    #     "Category:Tribal Culture of Meghalaya",
    #     "Category:Tribal Museums in India"
    # ],
    # "Science_and_Technology_Museum_Raipur_2": [
    #     "Category:Raipur",
    #     "Category:Science museums in India"
    # ],
    # "District_Museum_Berhampur": [
    #     "Category:Berhampur",
    #     "Category:Odisha",
    #     "Category:Museums in Odisha"
    # ],
    # "Zoological_Museum_Baripada": [
    #     "Category:Baripada",
    #     "Category:Zoology in India"
    # ],
    # "Odisha_Tribal_and_Folk_Art_Museum_Bhubaneswar_2": [
    #     "Category:Tribal Culture of Odisha",
    #     "Category:Bhubaneswar"
    # ],
    # "Ancient_Monuments_Museum_Patan_2": [
    #     "Category:Patan",
    #     "Category:Archaeology of Gujarat"
    # ],
    # "Museum_of_Gems_and_Jewellery_Surat_2": [
    #     "Category:Surat",
    #     "Category:Jewellery of India"
    # ],
    # "Bank_Note_Museum_Mumbai_2": [
    #     "Category:Numismatics of India",
    #     "Category:Mumbai"
    # ],
    # "State_Bank_Museum_Mumbai_2": [
    #     "Category:SBI",
    #     "Category:Mumbai"
    # ],
    # "Museum_of_Home_Plumbing_Mumbai_2": [
    #     "Category:Mumbai",
    #     "Category:Industry museums in India"
    # ],
    # "Museum_of_Traffic_Control_Mumbai_2": [
    #     "Category:Traffic in Mumbai",
    #     "Category:Mumbai"
    # ],
    # "Mangalore_Port_Museum_Mangalore_2": [
    #     "Category:Mangalore",
    #     "Category:Ports of India"
    # ],
    # "Richmond_Town_Museum_Bengaluru_2": [
    #     "Category:Bengaluru",
    #     "Category:Karnataka Culture"
    # ],
    # "Government_Museum_Mysuru_2": [
    #     "Category:Mysore",
    #     "Category:Government Museum Mysore"
    # ],
    # "Karnataka_Folk_Museum_Dandeli_2": [
    #     "Category:Dandeli",
    #     "Category:Folk Art of Karnataka"
    # ],
    # "Jain_Museum_Humcha_2": [
    #     "Category:Humcha",
    #     "Category:Jain Temples in India"
    # ],
    # "Pitalkhora_Museum_Yavatmal_2": [
    #     "Category:Archaeology of Maharashtra",
    #     "Category:Yavatmal"
    # ],
    # "Museum_of_Mahjong_Hyderabad_2": [
    #     "Category:Hyderabad",
    #     "Category:Games in India"
    # ],
    # "Eminence_Gallery_Hyderabad_2": [
    #     "Category:Hyderabad",
    #     "Category:Art galleries in India"
    # ],
    # "State_Archaeology_Museum_Hyderabad_2": [
    #     "Category:Archaeology of Telangana",
    #     "Category:Hyderabad"
    # ],
    # "Hyderabad_Film_Metro_Museum_2": [
    #     "Category:Cinema of Hyderabad",
    #     "Category:Film museums in India"
    # ],
    # "AP_State_Museum_and_Zoo_Hyderabad_2": [
    #     "Category:Hyderabad",
    #     "Category:Andhra Pradesh Heritage"
    # ],
    # "Chandra_Museum_Mandla_2": [
    #     "Category:Mandla",
    #     "Category:Tribal Culture Madhya Pradesh"
    # ],
    # "Panna_Natural_History_Museum_2": [
    #     "Category:Panna",
    #     "Category:Natural history museums in India"
    # ],
    # "Lok_Kala_Sanskriti_Sangrahalaya_Gwalior_2": [
    #     "Category:Gwalior",
    #     "Category:Madhya Pradesh Culture"
    # ],
    # "Heritage_Transport_Museum_Gurgaon_2": [
    #     "Category:Gurgaon",
    #     "Category:Transport Museums India"
    # ],
    # "Air_Force_Museum_Hyderabad_2": [
    #     "Category:Indian Air Force",
    #     "Category:Hyderabad"
    # ],
    # "Bombay_Dockyard_Museum_Mumbai_2": [
    #     "Category:Mumbai",
    #     "Category:Indian Navy"
    # ]
    #    "Delhi_Quilt_Museum_New_Delhi_2": [
    #     "Category:Delhi Quilt Museum",
    #     "Category:Quilt Museum, Delhi"
    # ],
    # "Nomadic_Textile_Museum_New_Delhi_2": [
    #     "Category:Nomadic Textile Museum",
    #     "Category:Nomadic Textile Museum, New Delhi"
    # ],
    # "National_Philatelic_Museum_New_Delhi_2": [
    #     "Category:National Philatelic Museum",
    #     "Category:National Philatelic Museum, New Delhi"
    # ],
    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi_2": [
    #     "Category:National Handicrafts & Handlooms Museum",
    #     "Category:Crafts Museum, Delhi"
    # ],
    # "Rail_Coach_Factory_Heritage_Museum_Rae_Bareli_2": [
    #     "Category:Rail Coach Factory Heritage Museum",
    #     "Category:Rail Coach Factory Museum, Rae Bareli"
    # ],
    # "Fatehpur_Sikri_Museum_2": [
    #     "Category:Fatehpur Sikri Museum",
    #     "Category:Fatehpur Sikri Archaeological Museum"
    # ],
    # "Galib_Ki_Haveli_Museum_Old_Delhi_2": [
    #     "Category:Ghalib ki Haveli",
    #     "Category:Ghalib Ki Haveli Museum"
    # ],
    # "Bloom_Art_Gallery_Meerut_2": [
    #     "Category:Bloom Art Gallery",
    #     "Category:Bloom Art Gallery, Meerut"
    # ],
    # "Lucknow_State_Museum_2": [
    #     "Category:Lucknow State Museum",
    #     "Category:State Museum, Lucknow"
    # ],
    # "City_Museum_Vadodara_2": [
    #     "Category:City Museum Vadodara",
    #     "Category:Vadodara City Museum"
    # ],
    # "Vadodara_Museum_and_Picture_Gallery_Vadodara_2": [
    #     "Category:Vadodara Museum and Picture Gallery",
    #     "Category:Vadodara Museum & Picture Gallery"
    # ],
    # "Tripura_Government_Museum_Agartala": [
    #     "Category:Tripura Government Museum",
    #     "Category:Tripura State Museum, Agartala"
    # ],
    # "Bomdila_District_Museum": [
    #     "Category:Bomdila District Museum",
    #     "Category:Bomdila Museum"
    # ],
    # "Ziro_District_Museum": [
    #     "Category:Ziro District Museum",
    #     "Category:Ziro Museum"
    # ],
    # "Hornbill_Festival_Ethnographic_Museum_Dimapur_2": [
    #     "Category:Hornbill Festival Ethnographic Museum",
    #     "Category:Hornbill Festival Museum Dimapur"
    # ],
    #   "Nagaland_State_Museum_Kohima": [
    #     "Category:Nagaland State Museum",
    #     "Category:Nagaland State Museum, Kohima"
    # ],
    # "Tikob_Heritage_Museum_Dimapur": [
    #     "Category:Tikob Heritage Museum",
    #     "Category:Tikob Heritage Museum, Dimapur"
    # ],
    # "Changthang_Wildlife_Sanctuary_Interpretation_Centre_Padum": [
    #     "Category:Changthang Wildlife Sanctuary Interpretation Centre",
    #     "Category:Changthang Interpretation Centre, Padum"
    # ],
    # "Ladakh_Folklore_Museum_Leh": [
    #     "Category:Ladakh Folklore Museum",
    #     "Category:Ladakh Folklore Museum, Leh"
    # ],
    # "Zanskar_Heritage_Museum_Padum": [
    #     "Category:Zanskar Heritage Museum",
    #     "Category:Zanskar Heritage Museum, Padum"
    # ],
    # "Museum_of_Kashmir_Arts_Srinagar": [
    #     "Category:Museum of Kashmir Arts",
    #     "Category:Museum of Kashmir Arts, Srinagar"
    # ],
    # "Indira_Gandhi_Memorial_Museum_Srinagar": [
    #     "Category:Indira Gandhi Memorial Museum",
    #     "Category:Indira Gandhi Memorial Museum, Srinagar"
    # ],
    # "Dogra_Art_Museum_Srinagar": [
    #     "Category:Dogra Art Museum",
    #     "Category:Dogra Art Museum, Srinagar"
    # ],
    # "Bihar_Museum_Annex_Patna_2": [
    #     "Category:Bihar Museum Annex",
    #     "Category:Bihar Museum Annex, Patna"
    # ],
    # "Paradise_Art_Gallery_Patna": [
    #     "Category:Paradise Art Gallery",
    #     "Category:Paradise Art Gallery, Patna"
    # ],
    # "Mahatma_Gandhi_Memorial_Museum_Rajkot": [
    #     "Category:Mahatma Gandhi Memorial Museum",
    #     "Category:Mahatma Gandhi Memorial Museum, Rajkot"
    # ],
    # "Gandhi_Memorial_Gandhinagar": [
    #     "Category:Gandhi Memorial",
    #     "Category:Gandhi Memorial, Gandhinagar"
    # ],
    # "Museum_of_Sacred_Arts_Guwahati": [
    #     "Category:Museum of Sacred Arts",
    #     "Category:Museum of Sacred Arts, Guwahati"
    # ],
    # "Museum_Malabar_Guruvayur": [
    #     "Category:Museum Malabar",
    #     "Category:Museum Malabar, Guruvayur"
    # ],
    # "Kerala_Spices_Museum_Kozhikode": [
    #     "Category:Kerala Spices Museum",
    #     "Category:Kerala Spices Museum, Kozhikode"
    # ],
    # "District_Museum_Biswanath": [
    #     "Category:District Museum, Biswanath",
    #     "Category:Biswanath District Museum"
    # ],
    # "District_Museum_Jorhat": [
    #     "Category:District Museum, Jorhat",
    #     "Category:Jorhat District Museum"
    # ],
    # "District_Museum_Silchar": [
    #     "Category:District Museum, Silchar",
    #     "Category:Silchar District Museum"
    # ],
    # "District_Museum_Dibrugarh": [
    #     "Category:District Museum, Dibrugarh",
    #     "Category:Dibrugarh District Museum"
    # ],
    # "Science_and_Technology_Museum_Siliguri": [
    #     "Category:Science & Technology Museum, Siliguri",
    #     "Category:Siliguri Science and Technology Museum"
    # ],
    # "Darjeeling_Himalayan_Railway_Museum": [
    #     "Category:Darjeeling Himalayan Railway Museum",
    #     "Category:Darjeeling Railway Museum"
    # ],
    # "Himalayan_Mountaineering_Institute_Museum_Darjeeling": [
    #     "Category:Himalayan Mountaineering Institute",
    #     "Category:Himalayan Mountaineering Institute Museum"
    # ],
    # "Nichugiri_Monastery_Museum_Darjeeling": [
    #     "Category:Nichugiri Monastery Museum",
    #     "Category:Nichugiri Monastery Museum, Darjeeling"
    # ],
    # "Zoological_Museum_Kolkata": [
    #     "Category:Zoological Museum, Kolkata",
    #     "Category:Zoological Museum Kolkata"
    # ],
    # "Bhandarkar_Oriental_Research_Institute_Museum_Pune": [
    #     "Category:Bhandarkar Oriental Research Institute",
    #     "Category:Bhandarkar Oriental Research Institute Museum"
    # ],
    # "Tilak_Museum_Pune": [
    #     "Category:Tilak Museum",
    #     "Category:Tilak Museum, Pune"
    # ],
    # "Raja_Dinkar_Kelkar_Museum_Pune": [
    #     "Category:Raja Dinkar Kelkar Museum",
    #     "Category:Raja Dinkar Kelkar Museum, Pune"
    # ],
    # "Lohagad_Fort_Museum_Matheran": [
    #     "Category:Lohagad Fort Museum",
    #     "Category:Lohagad Fort Museum, Matheran"
    # ],
    # "Deccan_College_Museum_Pune": [
    #     "Category:Deccan College Museum",
    #     "Category:Deccan College Museum, Pune"
    # ],
    # "Chhatrapati_Shivaji_Maharaj_Museum_of_Indian_Maritime_Heritage_Mumbai_2": [
    #     "Category:Chhatrapati Shivaji Maharaj Museum of Indian Maritime Heritage",
    #     "Category:Indian Maritime Heritage Museum, Mumbai"
    # ],
    # "Railway_Heritage_Centre_Chennai_2": [
    #     "Category:Railway Heritage Centre, Chennai",
    #     "Category:Railway Heritage Centre Chennai"
    # ],
    # "Government_Museum_Karur": [
    #     "Category:Government Museum, Karur",
    #     "Category:Government Museum Karur"
    # ],
    # "Museum_of_Photography_Pondicherry": [
    #     "Category:Museum of Photography, Pondicherry",
    #     "Category:Photography Museum Pondicherry"
    # ],
    # "Koraput_Tribal_Museum": [
    #     "Category:Koraput Tribal Museum",
    #     "Category:Koraput Tribal Museum, Koraput"
    # ],
    # "Hirapur_Tribal_Museum_Rourkela": [
    #     "Category:Hirapur Tribal Museum",
    #     "Category:Hirapur Tribal Museum, Rourkela"
    # ]
     # --- DELHI / NCR ---

    # "Delhi_Quilt_Museum_New_Delhi_2": [
    #     "Category:Quilts",
    #     "Category:Textile museums in India",
    #     "Category:Museums in Delhi"
    # ],

    # "Nomadic_Textile_Museum_New_Delhi_2": [
    #     "Category:Textiles of India",
    #     "Category:Textile museums in India",
    #     "Category:Museums in Delhi"
    # ],

    # "National_Philatelic_Museum_New_Delhi_2": [
    #     "Category:National Philatelic Museum (India)",
    #     "Category:Postage stamps of India",
    #     "Category:Philately of India",
    #     "Category:Museums in Delhi"
    # ],

    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi_2": [
    #     "Category:Crafts Museum, Delhi",
    #     "Category:Handicrafts of India",
    #     "Category:Textiles of India",
    #     "Category:Museums in Delhi"
    # ],

    # "Galib_Ki_Haveli_Museum_Old_Delhi_2": [
    #     "Category:Ghalib ki Haveli"
    # ],

    # "Bloom_Art_Gallery_Meerut_2": [
    #     "Category:Meerut",
    #     "Category:Art of Uttar Pradesh",
    #     "Category:Art galleries in India"
    # ],


    # # --- UTTAR PRADESH / RAE BARELI / LUCKNOW ---

    # "Rail_Coach_Factory_Heritage_Museum_Rae_Bareli_2": [
    #     "Category:Rail Coach Factory, Raebareli",
    #     "Category:Rail transport in India",
    #     "Category:Railway museums in India"
    # ],

    # "Fatehpur_Sikri_Museum_2": [
    #     "Category:Fatehpur Sikri",
    #     "Category:Archaeological Survey of India museums",
    #     "Category:Museums in Uttar Pradesh"
    # ],

    # "Lucknow_State_Museum_2": [
    #     "Category:State Museum, Lucknow",
    #     "Category:Museums in Uttar Pradesh",
    #     "Category:Culture of Lucknow"
    # ],


    # # --- GUJARAT / VADODARA / RAJKOT / GANDHINAGAR ---

    # "City_Museum_Vadodara_2": [
    #     "Category:Vadodara",
    #     "Category:Museums in Gujarat"
    # ],

    # "Vadodara_Museum_and_Picture_Gallery_Vadodara_2": [
    #     "Category:Baroda Museum & Picture Gallery",
    #     "Category:Vadodara Museum and Picture Gallery"
    # ],

    # "Mahatma_Gandhi_Memorial_Museum_Rajkot": [
    #     "Category:Rajkot",
    #     "Category:Mahatma Gandhi",
    #     "Category:Museums in Gujarat"
    # ],

    # "Gandhi_Memorial_Gandhinagar": [
    #     "Category:Gandhinagar",
    #     "Category:Mahatma Gandhi",
    #     "Category:Museums in Gujarat"
    # ],


    # # --- TRIPURA / ARUNACHAL / NAGALAND / LADAKH / NE STATES ---

    # "Tripura_Government_Museum_Agartala": [
    #     "Category:Agartala",
    #     "Category:Museums in Tripura"
    # ],

    # "Bomdila_District_Museum": [
    #     "Category:Bomdila",
    #     "Category:Museums in Arunachal Pradesh"
    # ],

    # "Ziro_District_Museum": [
    #     "Category:Ziro valley",
    #     "Category:Museums in Arunachal Pradesh"
    # ],

    # "Hornbill_Festival_Ethnographic_Museum_Dimapur_2": [
    #     "Category:Hornbill Festival",
    #     "Category:Dimapur",
    #     "Category:Culture of Nagaland"
    # ],

    # "Nagaland_State_Museum_Kohima": [
    #     "Category:Kohima",
    #     "Category:Museums in Nagaland",
    #     "Category:Culture of Nagaland"
    # ],

    # "Tikob_Heritage_Museum_Dimapur": [
    #     "Category:Dimapur",
    #     "Category:Culture of Nagaland"
    # ],

    # "Changthang_Wildlife_Sanctuary_Interpretation_Centre_Padum": [
    #     "Category:Changthang Wildlife Sanctuary",
    #     "Category:Wildlife sanctuaries of India",
    #     "Category:Ladakh"
    # ],

    # "Ladakh_Folklore_Museum_Leh": [
    #     "Category:Leh",
    #     "Category:Culture of Ladakh",
    #     "Category:Folk art of India"
    # ],

    # "Zanskar_Heritage_Museum_Padum": [
    #     "Category:Zanskar",
    #     "Category:Culture of Ladakh"
    # ],

    # "Museum_of_Kashmir_Arts_Srinagar": [
    #     "Category:Kashmir shawls",
    #     "Category:Art of Jammu and Kashmir",
    #     "Category:Srinagar"
    # ],

    # "Indira_Gandhi_Memorial_Museum_Srinagar": [
    #     "Category:Srinagar",
    #     "Category:Indira Gandhi"
    # ],


    # # --- BIHAR ---

    # "Bihar_Museum_Annex_Patna_2": [
    #     "Category:Bihar Museum",
    #     "Category:Museums in Patna"
    # ],

    # "Paradise_Art_Gallery_Patna": [
    #     "Category:Patna",
    #     "Category:Art of Bihar",
    #     "Category:Art galleries in India"
    # ],


    # # --- ASSAM / NORTH-EAST (MUSEUMS & DISTRICT MUSEUMS) ---

    # "Museum_of_Sacred_Arts_Guwahati": [
    #     "Category:Guwahati",
    #     "Category:Religion in Assam",
    #     "Category:Museums in Assam"
    # ],

    # "District_Museum_Biswanath": [
    #     "Category:Biswanath (Assam)",
    #     "Category:Museums in Assam"
    # ],

    # "District_Museum_Jorhat": [
    #     "Category:Jorhat",
    #     "Category:Museums in Assam"
    # ],

    # "District_Museum_Silchar": [
    #     "Category:Silchar",
    #     "Category:Museums in Assam"
    # ],

    # "District_Museum_Dibrugarh": [
    #     "Category:Dibrugarh",
    #     "Category:Museums in Assam"
    # ],

    # "Science_and_Technology_Museum_Siliguri": [
    #     "Category:Siliguri",
    #     "Category:Science museums in India"
    # ],

    # "Darjeeling_Himalayan_Railway_Museum": [
    #     "Category:Darjeeling Himalayan Railway",
    #     "Category:Rail transport in West Bengal"
    # ],

    # "Nichugiri_Monastery_Museum_Darjeeling": [
    #     "Category:Darjeeling",
    #     "Category:Buddhist monasteries in India"
    # ],


    # # --- WEST BENGAL / KOLKATA ---

    # "Zoological_Museum_Kolkata": [
    #     "Category:Zoological Survey of India",
    #     "Category:Kolkata",
    #     "Category:Zoology in India"
    # ],


    # # --- MAHARASHTRA (PUNE, MATHERAN, ETC.) ---

    # "Tilak_Museum_Pune": [
    #     "Category:Pune",
    #     "Category:Bal Gangadhar Tilak",
    #     "Category:Museums in Maharashtra"
    # ],

    # "Lohagad_Fort_Museum_Matheran": [
    #     "Category:Lohagad Fort",
    #     "Category:Forts in Maharashtra"
    # ],

    # "Deccan_College_Museum_Pune": [
    #     "Category:Deccan College",
    #     "Category:Pune",
    #     "Category:Archaeology of India"
    # ],

    # "Chhatrapati_Shivaji_Maharaj_Museum_of_Indian_Maritime_Heritage_Mumbai_2": [
    #     "Category:Indian Navy",
    #     "Category:Maritime history of India",
    #     "Category:Mumbai"
    # ],


    # # --- TAMIL NADU / PONDICHERRY ---

    # "Railway_Heritage_Centre_Chennai_2": [
    #     "Category:Rail transport in Chennai",
    #     "Category:Railway museums in India"
    # ],

    # "Government_Museum_Karur": [
    #     "Category:Karur",
    #     "Category:Museums in Tamil Nadu"
    # ],

    # "Museum_of_Photography_Pondicherry": [
    #     "Category:Puducherry",
    #     "Category:Photography in India",
    #     "Category:Art museums and galleries in India"
    # ],


    # # --- ODISHA ---

    # "Koraput_Tribal_Museum": [
    #     "Category:Koraput",
    #     "Category:Tribal culture of Odisha",
    #     "Category:Museums in Odisha"
    # ],

    # "Hirapur_Tribal_Museum_Rourkela": [
    #     "Category:Rourkela",
    #     "Category:Tribal culture of Odisha",
    #     "Category:Museums in Odisha"
    # ],

    # "Museum_Malabar_Guruvayur": [
    #     "Category:Guruvayur",
    #     "Category:Kerala",
    #     "Category:Museums in Kerala"
    # ],

    # "Kerala_Spices_Museum_Kozhikode": [
    #     "Category:Spices of India",
    #     "Category:Kozhikode",
    #     "Category:Agriculture museums in India"
    # ]
    #    "Chandannagar_Heritage_Museum": [
    #     "Category:Chandannagar Heritage Museum",
    #     "Category:Chandannagar Museum"
    # ],
    # "Birla_Industrial_and_Technological_Museum_Annex_Kolkata": [
    #     "Category:Birla Industrial & Technological Museum Annex",
    #     "Category:BITM Annex Kolkata"
    # ],
    # "Medieval_Interpretation_Centre_Chitradurga": [
    #     "Category:Medieval Interpretation Centre, Chitradurga",
    #     "Category:Chitradurga Medieval Interpretation Centre"
    # ],
    # "Belgaum_Military_Museum_Belagavi": [
    #     "Category:Belgaum Military Museum",
    #     "Category:Belgaum Military Museum, Belagavi"
    # ],
    # "Kadri_Manjunath_Temples_Museum_Mangalore": [
    #     "Category:Kadri Manjunath Temples Museum",
    #     "Category:Kadri Temple Museum Mangalore"
    # ],
    # "State_History_Museum_Bhopal": [
    #     "Category:State History Museum, Bhopal",
    #     "Category:State History Museum Bhopal"
    # ],
    # "Tribhuvan_Narayan_Singh_Regional_Museum_Raigarh": [
    #     "Category:Tribhuvan Narayan Singh Regional Museum",
    #     "Category:Tribhuvan Narayan Singh Museum Raigarh"
    # ],
    # "Central_Museum_Bilaspur": [
    #     "Category:Central Museum, Bilaspur",
    #     "Category:Bilaspur Central Museum"
    # ],
    # "Government_Museum_Bhilai": [
    #     "Category:Government Museum, Bhilai",
    #     "Category:Government Museum Bhilai"
    # ],
    # "Government_Museum_Rajnandgaon": [
    #     "Category:Government Museum, Rajnandgaon",
    #     "Category:Government Museum Rajnandgaon"
    # ],
    # "Government_Museum_Durg": [
    #     "Category:Government Museum, Durg",
    #     "Category:Government Museum Durg"
    # ],
    # "Government_Museum_Raipur_2": [
    #     "Category:Government Museum, Raipur",
    #     "Category:Government Museum Raipur"
    # ],
    # "Mandapeshwar_Caves_Museum_Borivali_East": [
    #     "Category:Mandapeshwar Caves Museum",
    #     "Category:Mandapeshwar Caves Museum, Borivali"
    # ],
    # "Hmuels_Museum_Shillong": [
    #     "Category:Hmuels Museum",
    #     "Category:Hmuels Museum, Shillong"
    # ],
    # "Shevgaon_Sugar_Museum_Shevgaon": [
    #     "Category:Shevgaon Sugar Museum",
    #     "Category:Shevgaon Sugar Museum, Shevgaon"
    # ],
    #  "Coal_Heritage_Museum_Kottagudda": [
    #     "Category:Coal Heritage Museum",
    #     "Category:Coal Heritage Museum Kottagudda"
    # ],

    # "Government_Museum_Thrissur": [
    #     "Category:Government Museum, Thrissur",
    #     "Category:Thrissur Government Museum"
    # ],

    # "Napier_Museum_Annex_TVM": [
    #     "Category:Napier Museum Annex",
    #     "Category:Napier Museum, Thiruvananthapuram"
    # ],

    # "Museum_of_Natural_History_Chandigarh": [
    #     "Category:Museum of Natural History Chandigarh",
    #     "Category:Chandigarh Natural History Museum"
    # ],

    # "Chandigarh_State_Museum": [
    #     "Category:Chandigarh State Museum"
    # ],

    # "Modern_History_Museum_Shimla": [
    #     "Category:Modern History Museum Shimla",
    #     "Category:Shimla History Museum"
    # ],

    # "Gandhi_Smriti_Sangrahalaya_Patiala": [
    #     "Category:Gandhi Smriti Sangrahalaya Patiala"
    # ],

    # "Rural_Life_Museum_Kailashpur": [
    #     "Category:Rural Life Museum Kailashpur"
    # ],

    # "Uttarakhand_Crafts_Museum_Dehradun": [
    #     "Category:Uttarakhand Crafts Museum",
    #     "Category:Crafts Museum Dehradun"
    # ],

    # "Buddhist_Arts_Museum_Rishikesh": [
    #     "Category:Buddhist Arts Museum Rishikesh"
    # ],

    # "Roshnai_Darwaza_Museum_Jaipur": [
    #     "Category:Roshnai Darwaza Museum Jaipur"
    # ],

    # "City_Palace_Museum_Jaipur_Annex": [
    #     "Category:City Palace Museum Jaipur",
    #     "Category:City Palace Museum Annex Jaipur"
    # ],

    # "Rajasthan_State_Museum_Jaipur_Annex": [
    #     "Category:Rajasthan State Museum Jaipur",
    #     "Category:Rajasthan State Museum Annex"
    # ],

    # "Albert_Hall_Museum_Annex_Jaipur": [
    #     "Category:Albert Hall Museum Annex Jaipur"
    # ],

    # "Ajmer_Government_Museum": [
    #     "Category:Ajmer Government Museum"
    # ],

    # "Pushkar_Sheep_Fair_Interpretation_Centre": [
    #     "Category:Pushkar Sheep Fair Interpretation Centre"
    # ],

    # "Gujari_Mahal_Archaeological_Museum_Gwalior": [
    #     "Category:Gujari Mahal Museum",
    #     "Category:Gujari Mahal Archaeological Museum"
    # ],

    # "Indore_Museum": [
    #     "Category:Indore Museum"
    # ],

    # "Ujjain_Archaeological_Museum": [
    #     "Category:Ujjain Archaeological Museum"
    # ],

    # "Khajuraho_Archaeological_Museum": [
    #     "Category:Khajuraho Archaeological Museum"
    # ],

    # "Gwalior_Fort_Museum": [
    #     "Category:Gwalior Fort Museum"
    # ],

    # "Orchha_State_Archaeological_Museum": [
    #     "Category:Orchha Archaeological Museum",
    #     "Category:Orchha State Archaeological Museum"
    # ],

    # "Saugor_Museum_Sagar": [
    #     "Category:Saugor Museum"
    # ],

    # "Bhopal_Tribal_Museum": [
    #     "Category:Bhopal Tribal Museum",
    #     "Category:Tribal Museum Bhopal"
    # ],

    # "Governors_House_Museum_Bhopal": [
    #     "Category:Governor's House Museum Bhopal"
    # ],

    # "Itarsi_Railway_Heritage_Centre": [
    #     "Category:Itarsi Railway Heritage Centre"
    # ],

    # "Museum_of_Indology_BHU": [
    #     "Category:Museum of Indology BHU",
    #     "Category:Banaras Hindu University Museum"
    # ],

    # "Sarnath_Museum": [
    #     "Category:Sarnath Museum"
    # ],

    # "Taj_Interpretation_Centre_Agra": [
    #     "Category:Taj Interpretation Centre"
    # ],

    # "Agra_Fort_Museum": [
    #     "Category:Agra Fort Museum"
    # ],

    # "Mathura_Museum": [
    #     "Category:Mathura Museum"
    # ],

    # "Meerut_Museum": [
    #     "Category:Meerut Museum"
    # ]
    #  "Chandannagar_Heritage_Museum": [
    #     "Category:Chandannagar",
    #     "Category:French India",
    #     "Category:Heritage of West Bengal"
    # ],
    # "Birla_Industrial_and_Technological_Museum_Annex_Kolkata": [
    #     "Category:Birla Industrial & Technological Museum",
    #     "Category:Science museums in India",
    #     "Category:Kolkata"
    # ],
    # "Medieval_Interpretation_Centre_Chitradurga": [
    #     "Category:Chitradurga Fort",
    #     "Category:Chitradurga",
    #     "Category:Karnataka history"
    # ],
    # "Belgaum_Military_Museum_Belagavi": [
    #     "Category:Belgaum",
    #     "Category:Indian Army",
    #     "Category:Military history of India"
    # ],
    # "Kadri_Manjunath_Temples_Museum_Mangalore": [
    #     "Category:Kadri Manjunath Temple",
    #     "Category:Mangalore",
    #     "Category:Karnataka Temples"
    # ],
    # "State_History_Museum_Bhopal": [
    #     "Category:Bhopal",
    #     "Category:Madhya Pradesh history",
    #     "Category:Madhya Pradesh archaeology"
    # ],
    # "Tribhuvan_Narayan_Singh_Regional_Museum_Raigarh": [
    #     "Category:Raigarh",
    #     "Category:Chhattisgarh culture"
    # ],
    # "Central_Museum_Bilaspur": [
    #     "Category:Bilaspur",
    #     "Category:Chhattisgarh archaeology"
    # ],
    # "Government_Museum_Bhilai": [
    #     "Category:Bhilai",
    #     "Category:Chhattisgarh"
    # ],
    # "Government_Museum_Rajnandgaon": [
    #     "Category:Rajnandgaon",
    #     "Category:Chhattisgarh"
    # ],
    # "Government_Museum_Durg": [
    #     "Category:Durg",
    #     "Category:Chhattisgarh"
    # ],
    # "Government_Museum_Raipur_2": [
    #     "Category:Raipur",
    #     "Category:Chhattisgarh culture"
    # ],
    # "Mandapeshwar_Caves_Museum_Borivali_East": [
    #     "Category:Mandapeshwar Caves",
    #     "Category:Borivali",
    #     "Category:Mumbai caves"
    # ],
    # "Hmuels_Museum_Shillong": [
    #     "Category:Shillong",
    #     "Category:Meghalaya culture"
    # ],
    # "Shevgaon_Sugar_Museum_Shevgaon": [
    #     "Category:Sugar industry in India",
    #     "Category:Ahmednagar"
    # ],
    # "Coal_Heritage_Museum_Kottagudda": [
    #     "Category:Coal mining in India",
    #     "Category:Karnataka"
    # ],
    # "Government_Museum_Thrissur": [
    #     "Category:Thrissur",
    #     "Category:Kerala history"
    # ],
    # "Napier_Museum_Annex_TVM": [
    #     "Category:Napier Museum",
    #     "Category:Thiruvananthapuram museums"
    # ],
    # "Museum_of_Natural_History_Chandigarh": [
    #     "Category:Chandigarh",
    #     "Category:Natural history of India"
    # ],
    # "Chandigarh_State_Museum": [
    #     "Category:Chandigarh",
    #     "Category:Museums in Chandigarh"
    # ],
    # "Modern_History_Museum_Shimla": [
    #     "Category:Shimla",
    #     "Category:Himachal Pradesh history"
    # ],
    # "Gandhi_Smriti_Sangrahalaya_Patiala": [
    #     "Category:Patiala",
    #     "Category:Gandhi museums"
    # ],
    # "Rural_Life_Museum_Kailashpur": [
    #     "Category:Rural India",
    #     "Category:Ethnology of India"
    # ],
    # "Uttarakhand_Crafts_Museum_Dehradun": [
    #     "Category:Dehradun",
    #     "Category:Uttarakhand handicrafts"
    # ],
    # "Buddhist_Arts_Museum_Rishikesh": [
    #     "Category:Buddhist art",
    #     "Category:Rishikesh"
    # ],
    # "Roshnai_Darwaza_Museum_Jaipur": [
    #     "Category:Jaipur architecture",
    #     "Category:Rajasthan gates and monuments"
    # ],
    # "City_Palace_Museum_Jaipur_Annex": [
    #     "Category:City Palace, Jaipur",
    #     "Category:Rajasthan palaces"
    # ],
    # "Rajasthan_State_Museum_Jaipur_Annex": [
    #     "Category:Jaipur",
    #     "Category:Rajasthan State Museum"
    # ],
    # "Albert_Hall_Museum_Annex_Jaipur": [
    #     "Category:Albert Hall Museum",
    #     "Category:Jaipur"
    # ],
    # "Ajmer_Government_Museum": [
    #     "Category:Ajmer",
    #     "Category:Rajasthan archaeology"
    # ],
    # "Pushkar_Sheep_Fair_Interpretation_Centre": [
    #     "Category:Pushkar",
    #     "Category:Pushkar Fair",
    #     "Category:Rajasthan festivals"
    # ],
    # "Indore_Museum": [
    #     "Category:Indore",
    #     "Category:Madhya Pradesh archaeology"
    # ],
    # "Ujjain_Archaeological_Museum": [
    #     "Category:Ujjain",
    #     "Category:Archaeological museums in India"
    # ],
    # "Khajuraho_Archaeological_Museum": [
    #     "Category:Khajuraho",
    #     "Category:Khajuraho temples"
    # ],
    # "Gwalior_Fort_Museum": [
    #     "Category:Gwalior Fort",
    #     "Category:Gwalior"
    # ],
    # "Orchha_State_Archaeological_Museum": [
    #     "Category:Orchha",
    #     "Category:Bundelkhand"
    # ],
    # "Saugor_Museum_Sagar": [
    #     "Category:Sagar (MP)",
    #     "Category:Madhya Pradesh museums"
    # ],
    # "Governors_House_Museum_Bhopal": [
    #     "Category:Bhopal",
    #     "Category:Governor House Bhopal"
    # ],
    # "Itarsi_Railway_Heritage_Centre": [
    #     "Category:Itarsi Junction",
    #     "Category:Railways of India"
    # ],
    # "Museum_of_Indology_BHU": [
    #     "Category:Banaras Hindu University",
    #     "Category:Indology"
    # ],
    # "Taj_Interpretation_Centre_Agra": [
    #     "Category:Taj Mahal",
    #     "Category:Agra"
    # ],
    # "Agra_Fort_Museum": [
    #     "Category:Agra Fort",
    #     "Category:Agra"
    # ],
    # "Mathura_Museum": [
    #     "Category:Mathura",
    #     "Category:Braj culture"
    # ],
    # "Meerut_Museum": [
    #     "Category:Meerut",
    #     "Category:Uttar Pradesh museums"
    # ]
    #     "Noida_Museum_Architecture_Centre": [
    #     "Category:Noida Architecture Museum"
    # ],

    # "Ghaziabad_Archaeological_Museum": [
    #     "Category:Ghaziabad Archaeological Museum"
    # ],

    # "Gandhi_Smriti_New_Delhi": [
    #     "Category:Gandhi Smriti",
    #     "Category:Gandhi Smriti New Delhi"
    # ],

    # "Nehru_Memorial_Museum_and_Library": [
    #     "Category:Nehru Memorial Museum & Library"
    # ],

    # "Indira_Gandhi_Memorial_Museum_Delhi": [
    #     "Category:Indira Gandhi Memorial Museum",
    #     "Category:Indira Gandhi Museum Delhi"
    # ],

    # "Bhaktivedanta_Swami_Prabhupada_Museum_Mayapur": [
    #     "Category:Bhaktivedanta Swami Prabhupada Museum"
    # ],

    # "Hopetoun_Tea_Museum_Darjeeling": [
    #     "Category:Hopetoun Tea Museum"
    # ],

    # "Kabi_Kahini_Literary_Museum_Malda": [
    #     "Category:Kabi Kahini Literary Museum"
    # ],

    # "Medieval_Interpretation_Centre_Rajasthan": [
    #     "Category:Medieval Interpretation Centre Rajasthan"
    # ],

    # "Heritage_Interpretation_Centre_Mysore": [
    #     "Category:Heritage Interpretation Centre Mysore"
    # ],

    # "Shivaji_Smarak_Museum_Mumbai": [
    #     "Category:Shivaji Smarak Museum"
    # ],

    # "Elephanta_Cave_Museum": [
    #     "Category:Elephanta Caves Museum"
    # ],

    # "Netravati_Art_Gallery_Mangalore": [
    #     "Category:Netravati Art Gallery"
    # ],

    # "Fishery_Museum_Panaji": [
    #     "Category:Fishery Museum Panaji"
    # ],

    # "India_Civil_Aviation_Heritage_Museum_Delhi": [
    #     "Category:India Civil Aviation Heritage Museum"
    # ],

    # "Indian_Coast_Guard_Marina_Museum_Karwar": [
    #     "Category:Indian Coast Guard Museum",
    #     "Category:Coast Guard Marina Museum Karwar"
    # ],

    # "Indian_Navy_Museum_Cochin": [
    #     "Category:Indian Navy Museum Cochin"
    # ],

    # "Central_Reserve_Police_Force_Museum_Dehradun": [
    #     "Category:CRPF Museum Dehradun",
    #     "Category:Central Reserve Police Force Museum"
    # ],
    # "Coal_Heritage_Museum_Kottagudda": [
    #     "Category:Coal Heritage Museum Kottagudda",
    #     "Category:Coal Heritage Museum"
    # ],
    # "Government_Museum_Thrissur": [
    #     "Category:Government Museum Thrissur",
    #     "Category:Thrissur Government Museum"
    # ],
    # "Napier_Museum_Annex_Thiruvananthapuram": [
    #     "Category:Napier Museum Annex",
    #     "Category:Napier Museum Thiruvananthapuram"
    # ],
    # "Museum_of_Natural_History_Chandigarh": [
    #     "Category:Museum of Natural History Chandigarh"
    # ],
    # "Chandigarh_State_Museum": [
    #     "Category:Chandigarh State Museum"
    # ],
    # "Modern_History_Museum_Shimla": [
    #     "Category:Modern History Museum Shimla"
    # ],
    # "Gandhi_Smriti_Sangrahalaya_Patiala": [
    #     "Category:Gandhi Smriti Sangrahalaya Patiala"
    # ],
    # "Rural_Life_Museum_Kailashpur": [
    #     "Category:Rural Life Museum Kailashpur"
    # ],
    # "Uttarakhand_Crafts_Museum_Dehradun": [
    #     "Category:Uttarakhand Crafts Museum"
    # ],
    # "Buddhist_Arts_Museum_Rishikesh": [
    #     "Category:Buddhist Arts Museum Rishikesh"
    # ],
    # "Roshnai_Darwaza_Museum_Jaipur": [
    #     "Category:Roshnai Darwaza Museum"
    # ],
    # "City_Palace_Museum_Jaipur_Annex": [
    #     "Category:City Palace Museum Jaipur"
    # ],
    # "Rajasthan_State_Museum_Jaipur_Annex": [
    #     "Category:Rajasthan State Museum Jaipur"
    # ],
    # "Albert_Hall_Museum_Annex_Jaipur": [
    #     "Category:Albert Hall Museum Jaipur"
    # ],
    # "Ajmer_Government_Museum": [
    #     "Category:Ajmer Government Museum"
    # ],
    # "Pushkar_Sheep_Fair_Interpretation_Centre": [
    #     "Category:Pushkar Sheep Fair Interpretation Centre"
    # ],
    # "Gujari_Mahal_Archaeological_Museum_Gwalior": [
    #     "Category:Gujari Mahal Museum"
    # ],
    # "Indore_Museum": [
    #     "Category:Indore Museum"
    # ],
    # "Ujjain_Archaeological_Museum": [
    #     "Category:Ujjain Archaeological Museum"
    # ],
    # "Khajuraho_Archaeological_Museum": [
    #     "Category:Khajuraho Archaeological Museum"
    # ],
    # "Gwalior_Fort_Museum": [
    #     "Category:Gwalior Fort Museum"
    # ],
    # "Orchha_State_Archaeological_Museum": [
    #     "Category:Orchha Archaeological Museum"
    # ],
    # "Saugor_Museum_Sagar": [
    #     "Category:Saugor Museum"
    # ],
    # "Bhopal_Tribal_Museum": [
    #     "Category:Bhopal Tribal Museum"
    # ],
    # "Governors_House_Museum_Bhopal": [
    #     "Category:Governor's House Museum Bhopal"
    # ],
    # "Itarsi_Railway_Heritage_Centre": [
    #     "Category:Itarsi Railway Heritage Centre"
    # ],
    # "Museum_of_Indology_BHU_Varanasi": [
    #     "Category:Museum of Indology BHU"
    # ],
    # "Sarnath_Museum": [
    #     "Category:Sarnath Museum"
    # ],
    # "Taj_Interpretation_Centre_Agra": [
    #     "Category:Taj Interpretation Centre"
    # ],
    # "Agra_Fort_Museum": [
    #     "Category:Agra Fort Museum"
    # ],
    # "Mathura_Museum": [
    #     "Category:Mathura Museum"
    # ],
    # "Meerut_Museum": [
    #     "Category:Meerut Museum"
    # ],
    # "Noida_Museum_Architecture_Centre": [
    #     "Category:Noida Museum Architecture Centre"
    # ],
    # "Ghaziabad_Archaeological_Museum": [
    #     "Category:Ghaziabad Archaeological Museum"
    # ],
    # "Gandhi_Smriti_New_Delhi": [
    #     "Category:Gandhi Smriti"
    # ],
    # "Nehru_Memorial_Museum_Library": [
    #     "Category:Nehru Memorial Museum and Library"
    # ],
    # "Indira_Gandhi_Memorial_Museum_New_Delhi": [
    #     "Category:Indira Gandhi Memorial Museum New Delhi"
    # ],
    # "Bhaktivedanta_Swami_Prabhupada_Museum_Mayapur": [
    #     "Category:Bhaktivedanta Swami Prabhupada Museum"
    # ],
    # "Hopetoun_Tea_Museum_Darjeeling": [
    #     "Category:Hopetoun Tea Museum"
    # ],
    # "Kabi_Kahini_Literary_Museum_Malda": [
    #     "Category:Kabi Kahini Literary Museum"
    # ],
    # "Medieval_Interpretation_Centre_Rajasthan": [
    #     "Category:Medieval Interpretation Centre Rajasthan"
    # ]
    #  "Noida_Museum_Architecture_Centre": [
    #     "Category:Noida",
    #     "Category:Architecture of Uttar Pradesh"
    # ],
    # "Ghaziabad_Archaeological_Museum": [
    #     "Category:Ghaziabad",
    #     "Category:Archaeology of Uttar Pradesh"
    # ],
    # "Gandhi_Smriti_New_Delhi": [
    #     "Category:Gandhi Smriti",
    #     "Category:Gandhi museums in India",
    #     "Category:Gandhi in Delhi"
    # ],
    # "Nehru_Memorial_Museum_and_Library": [
    #     "Category:Nehru Memorial Museum & Library",
    #     "Category:Nehru Memorial Museum",
    #     "Category:Teen Murti House"
    # ],
    # "Indira_Gandhi_Memorial_Museum_Delhi": [
    #     "Category:Indira Gandhi Memorial Museum",
    #     "Category:Indira Gandhi",
    #     "Category:Delhi museums"
    # ],
    # "Bhaktivedanta_Swami_Prabhupada_Museum_Mayapur": [
    #     "Category:Mayapur",
    #     "Category:ISKCON",
    #     "Category:Hare Krishna movement"
    # ],
    # "Hopetoun_Tea_Museum_Darjeeling": [
    #     "Category:Darjeeling tea",
    #     "Category:Darjeeling",
    #     "Category:Tea estates in India"
    # ],
    # "Kabi_Kahini_Literary_Museum_Malda": [
    #     "Category:Malda",
    #     "Category:Bengali literature"
    # ],
    # "Medieval_Interpretation_Centre_Rajasthan": [
    #     "Category:Rajasthan history",
    #     "Category:Medieval India"
    # ],
    # "Heritage_Interpretation_Centre_Mysore": [
    #     "Category:Mysore",
    #     "Category:Heritage of Karnataka"
    # ],
    # "Shivaji_Smarak_Museum_Mumbai": [
    #     "Category:Shivaji",
    #     "Category:Shivaji memorials",
    #     "Category:Mumbai monuments"
    # ],
    # "Elephanta_Cave_Museum": [
    #     "Category:Elephanta Caves",
    #     "Category:Mumbai caves",
    #     "Category:UNESCO World Heritage Sites in India"
    # ],
    # "Netravati_Art_Gallery_Mangalore": [
    #     "Category:Mangalore",
    #     "Category:Art of Karnataka"
    # ],
    # "Fishery_Museum_Panaji": [
    #     "Category:Panaji",
    #     "Category:Fisheries of India",
    #     "Category:Goa museums"
    # ],
    # "India_Civil_Aviation_Heritage_Museum_Delhi": [
    #     "Category:Indian aviation",
    #     "Category:Airports Authority of India",
    #     "Category:Delhi museums"
    # ],
    # "Indian_Coast_Guard_Marina_Museum_Karwar": [
    #     "Category:Indian Coast Guard",
    #     "Category:Karwar"
    # ],
    # "Indian_Navy_Museum_Cochin": [
    #     "Category:Indian Navy",
    #     "Category:Kochi",
    #     "Category:Naval museums"
    # ],
    # "Central_Reserve_Police_Force_Museum_Dehradun": [
    #     "Category:CRPF",
    #     "Category:Dehradun",
    #     "Category:Military of India"
    # ],

    # # These below were repeated – final working versions:
    # "Coal_Heritage_Museum_Kottagudda": [
    #     "Category:Coal mining in India",
    #     "Category:Karnataka"
    # ],
    # "Government_Museum_Thrissur": [
    #     "Category:Thrissur",
    #     "Category:Kerala history"
    # ],
    # "Napier_Museum_Annex_Thiruvananthapuram": [
    #     "Category:Napier Museum",
    #     "Category:Thiruvananthapuram"
    # ],
    # "Museum_of_Natural_History_Chandigarh": [
    #     "Category:Chandigarh",
    #     "Category:Natural history museums"
    # ],
    # "Chandigarh_State_Museum": [
    #     "Category:Chandigarh museums",
    #     "Category:Chandigarh"
    # ],
    # "Modern_History_Museum_Shimla": [
    #     "Category:Shimla",
    #     "Category:Himachal Pradesh history"
    # ],
    # "Gandhi_Smriti_Sangrahalaya_Patiala": [
    #     "Category:Patiala",
    #     "Category:Gandhi museums in India"
    # ],
    # "Rural_Life_Museum_Kailashpur": [
    #     "Category:Rural India",
    #     "Category:Folk culture of India"
    # ],
    # "Uttarakhand_Crafts_Museum_Dehradun": [
    #     "Category:Uttarakhand Handicrafts",
    #     "Category:Dehradun"
    # ],
    # "Buddhist_Arts_Museum_Rishikesh": [
    #     "Category:Rishikesh",
    #     "Category:Buddhist art"
    # ],
    # "Roshnai_Darwaza_Museum_Jaipur": [
    #     "Category:Jaipur",
    #     "Category:Rajasthan gates"
    # ],
    # "City_Palace_Museum_Jaipur_Annex": [
    #     "Category:City Palace, Jaipur",
    #     "Category:Jaipur museums"
    # ],
    # "Rajasthan_State_Museum_Jaipur_Annex": [
    #     "Category:Rajasthan museums",
    #     "Category:Jaipur"
    # ],
    # "Albert_Hall_Museum_Annex_Jaipur": [
    #     "Category:Albert Hall Museum",
    #     "Category:Jaipur"
    # ],
    # "Ajmer_Government_Museum": [
    #     "Category:Ajmer",
    #     "Category:Rajasthan archaeology"
    # ],
    # "Pushkar_Sheep_Fair_Interpretation_Centre": [
    #     "Category:Pushkar Fair",
    #     "Category:Pushkar"
    # ],
    # "Gujari_Mahal_Archaeological_Museum_Gwalior": [
    #     "Category:Gujari Mahal",
    #     "Category:Gwalior Fort"
    # ],
    # "Indore_Museum": [
    #     "Category:Indore",
    #     "Category:Madhya Pradesh museums"
    # ],
    # "Ujjain_Archaeological_Museum": [
    #     "Category:Ujjain",
    #     "Category:Archaeological museums"
    # ],
    # "Khajuraho_Archaeological_Museum": [
    #     "Category:Khajuraho",
    #     "Category:Khajuraho temples"
    # ],
    # "Gwalior_Fort_Museum": [
    #     "Category:Gwalior Fort",
    #     "Category:Gwalior"
    # ],
    # "Orchha_State_Archaeological_Museum": [
    #     "Category:Orchha",
    #     "Category:Madhya Pradesh archaeology"
    # ],
    # "Saugor_Museum_Sagar": [
    #     "Category:Sagar (MP)",
    #     "Category:Madhya Pradesh"
    # ],
    # "Bhopal_Tribal_Museum": [
    #     "Category:Tribal Museum Bhopal",
    #     "Category:Tribal culture of India"
    # ],
    # "Governors_House_Museum_Bhopal": [
    #     "Category:Bhopal",
    #     "Category:Madhya Pradesh history"
    # ],
    # "Itarsi_Railway_Heritage_Centre": [
    #     "Category:Itarsi",
    #     "Category:Indian Railways"
    # ],
    # "Museum_of_Indology_BHU_Varanasi": [
    #     "Category:BHU",
    #     "Category:Varanasi"
    # ],
    # "Taj_Interpretation_Centre_Agra": [
    #     "Category:Taj Mahal",
    #     "Category:Agra"
    # ],
    # "Agra_Fort_Museum": [
    #     "Category:Agra Fort",
    #     "Category:Agra"
    # ],
    # "Mathura_Museum": [
    #     "Category:Mathura",
    #     "Category:Braj region"
    # ],
    # "Meerut_Museum": [
    #     "Category:Meerut",
    #     "Category:Uttar Pradesh museums"
    # ],
    # "Nehru_Memorial_Museum_Library": [
    #     "Category:Nehru Memorial Museum & Library",
    #     "Category:Teen Murti House"
    # ],
    # "Indira_Gandhi_Memorial_Museum_New_Delhi": [
    #     "Category:Indira Gandhi Memorial Museum",
    #     "Category:Delhi museums"
    # ]
      # ------------- DELHI / GANDHI / NEHRU -------------
    # Gandhi Smriti → Commons moved the media to "Birla House"
    # "Gandhi_Smriti_New_Delhi": [
    #     "Category:Birla House",          # actual Commons category with photos :contentReference[oaicite:0]{index=0}
    # ],

    # # Old Nehru Memorial Museum & Library → now Prime Ministers' Museum and Library Society
    # # Category:Nehru Memorial Museum & Library is a redirect and should be empty. :contentReference[oaicite:1]{index=1}
    # "Nehru_Memorial_Museum_Library": [
    #     "Category:Prime Ministers' Museum and Library Society",
    # ],
    # "Nehru_Memorial_Museum_and_Library": [
    #     "Category:Prime Ministers' Museum and Library Society",
    # ],

    # # Indira Gandhi Memorial Museum, New Delhi
    # # Media is under "Indira Gandhi Memorial" (the museum + memorial) :contentReference[oaicite:2]{index=2}
    # "Indira_Gandhi_Memorial_Museum_New_Delhi": [
    #     "Category:Indira Gandhi Memorial",
    # ],
    # "Indira_Gandhi_Memorial_Museum_Delhi": [
    #     "Category:Indira Gandhi Memorial",
    # ],

    # # ------------- JAIPUR / RAJASTHAN -------------
    # # City Palace Museum Jaipur Annex – use the main City Palace category
    # # Correct Commons name uses parentheses, not a comma. :contentReference[oaicite:3]{index=3}
    # "City_Palace_Museum_Jaipur_Annex": [
    #     "Category:City Palace (Jaipur)",
    # ],

    # # Medieval Interpretation Centre, Rajasthan – it is the interpretation centre at Jantar Mantar Jaipur :contentReference[oaicite:4]{index=4}
    # "Medieval_Interpretation_Centre_Rajasthan": [
    #     "Category:Jantar Mantar (Jaipur)",
    # ],

    # # ------------- OTHER ENTRIES FROM YOUR LOG -------------
    # # India Civil Aviation Heritage Museum Delhi – this one already worked (you got 1 image),
    # # but just to be explicit and stable:
    # "India_Civil_Aviation_Heritage_Museum_Delhi": [
    #     "Category:Indian aviation",
    #     "Category:Airports Authority of India",   # where your Paintings_in_Ayodhya_Airport.jpg came from :contentReference[oaicite:5]{index=5}
    # ]
    #   "Heritage_Interpretation_Centre_Mysore": [
    #     "Category:Heritage Interpretation Centre Mysore"
    # ],
    # "Shivaji_Smarak_Museum_Bombay": [
    #     "Category:Shivaji Smarak Museum"
    # ],
    # "Elephanta_Cave_Museum": [
    #     "Category:Elephanta Cave Museum"
    # ],
    # "Netravati_Art_Gallery_Mangalore": [
    #     "Category:Netravati Art Gallery"
    # ],
    # "Fishery_Museum_Panaji": [
    #     "Category:Fishery Museum Panaji"
    # ],
    # "India_Civil_Aviation_Heritage_Museum": [
    #     "Category:India Civil Aviation Heritage Museum"
    # ],
    # "Indian_Coast_Guard_Marina_Museum_Karwar": [
    #     "Category:Indian Coast Guard Marina Museum"
    # ],
    # "Indian_Navy_Museum_Kochi": [
    #     "Category:Indian Navy Museum Kochi"
    # ],
    # "CRPF_Museum_Dehradun": [
    #     "Category:CRPF Museum Dehradun"
    # ],
    # "Border_Security_Force_Museum_Ghumarwin": [
    #     "Category:Border Security Force Museum"
    # ],
    # "Tibetan_Handicrafts_Museum_McLeod_Ganj": [
    #     "Category:Tibetan Handicrafts Museum"
    # ],
    # "Ford_India_Heritage_Research_Centre": [
    #     "Category:Ford India Heritage and Research Centre"
    # ],
    # "Amdavad_ni_Gufa_Museum": [
    #     "Category:Amdavad ni Gufa"
    # ],
    # "Vidyapith_Karshak_Darshan_Anand": [
    #     "Category:Vidyapith Karshak Darshan"
    # ],
    # "Shilpgram_Udaipur": [
    #     "Category:Shilpgram Udaipur"
    # ],
    # "Black_History_Museum_Shillong": [
    #     "Category:Black History Museum Shillong"
    # ],
    # "Automotive_Heritage_Museum_Mysuru": [
    #     "Category:Automotive Heritage Museum Mysuru"
    # ],
    # "Regional_Science_Centre_Allahabad": [
    #     "Category:Regional Science Centre Allahabad"
    # ],
    # "Sawai_Ram_Singh_Museum_Jaipur": [
    #     "Category:Sawai Ram Singh Museum"
    # ],
    # "Punjab_Rural_Heritage_Museum_Ludhiana": [
    #     "Category:Punjab Rural Heritage Museum"
    # ],
    # "Gurugram_Heritage_Interpretation_Centre": [
    #     "Category:Gurugram Heritage Interpretation Centre"
    # ],
    # "Folk_Museum_Patiala": [
    #     "Category:Folk Museum Patiala"
    # ],
    # "Sri_Ramanuja_Museum_Salem": [
    #     "Category:Sri Ramanuja Museum"
    # ],
    # "Polonia_Archaeological_Museum_Assam": [
    #     "Category:Polonia Archaeological Museum"
    # ],
    # "Museum_of_Folk_and_Tribal_Art_Delhi": [
    #     "Category:Museum of Folk and Tribal Art Delhi"
    # ],
    # "Thanjavur_Art_Gallery": [
    #     "Category:Thanjavur Art Gallery"
    # ],
    # "Government_Museum_and_Art_Gallery_Chennai": [
    #     "Category:Government Museum Chennai"
    # ],
    # "Central_Museum_Ahmedabad": [
    #     "Category:Central Museum Ahmedabad"
    # ],
    # "Gujarat_Science_City": [
    #     "Category:Gujarat Science City"
    # ],
    # "Sardar_Vallabhbhai_Patel_Museum_Surat": [
    #     "Category:Sardar Vallabhbhai Patel Museum Surat"
    # ],
    # "Bombay_Natural_History_Society_Museum": [
    #     "Category:Bombay Natural History Society Museum"
    # ],
    # "Indian_National_Army_Museum": [
    #     "Category:Indian National Army Museum"
    # ],
    # "Tribal_Museum_Itanagar": [
    #     "Category:Tribal Museum Itanagar"
    # ],
    # "Manipur_State_Museum": [
    #     "Category:Manipur State Museum"
    # ],
    # "Archaeological_Museum_Patna": [
    #     "Category:Archaeological Museum Patna"
    # ],
    # "Bhopal_Museum": [
    #     "Category:Bhopal Museum"
    # ],
    # "Museum_of_Indian_Railways": [
    #     "Category:Museum of Indian Railways"
    # ],
    # "Goa_State_Museum": [
    #     "Category:Goa State Museum"
    # ],
    # "Museum_of_Goa": [
    #     "Category:Museum of Goa"
    # ],
    # "Haryana_State_Museum_Chandigarh": [
    #     "Category:Haryana State Museum"
    # ],
    # "State_Museum_Bhubaneswar": [
    #     "Category:State Museum Bhubaneswar"
    # ],
    # "Vikram_Sarabhai_Space_Exhibition_Centre": [
    #     "Category:Vikram Sarabhai Space Exhibition Centre"
    # ],
    # "Museum_of_Tibetan_Culture_Dharamshala": [
    #     "Category:Museum of Tibetan Culture Dharamshala"
    # ],
    # "Museum_of_Art_and_Archaeology_Varanasi": [
    #     "Category:Museum of Art and Archaeology Varanasi"
    # ],
    # "Kushinagar_Museum": [
    #     "Category:Kushinagar Museum"
    # ],
    #   "Sanskritik_Museum_Udaipur": [
    #     "Category:Sanskritik Museum",
    #     "Category:Sanskritik Museum, Udaipur"
    # ],
    # "Rabindra_Bhavan_Museum_Kolkata": [
    #     "Category:Rabindra Bhavan Museum",
    #     "Category:Rabindra Bhavan, Kolkata"
    # ],
    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi": [
    #     "Category:National Handicrafts & Handlooms Museum",
    #     "Category:National Handicrafts and Handlooms Museum, New Delhi"
    # ],
    # "Folk_Art_Museum_Jaipur": [
    #     "Category:Folk Art Museum",
    #     "Category:Folk Art Museum, Jaipur"
    # ],
    # "Mahakavi_Kalidas_Sangrahalaya_Ujjain": [
    #     "Category:Mahakavi Kalidas Sangrahalaya",
    #     "Category:Kalidas Sangrahalaya Ujjain"
    # ],
    # "Science_City_Kolkata": [
    #     "Category:Science City, Kolkata",
    #     "Category:Science City Kolkata"
    # ],
    # "National_Gallery_of_Modern_Art_New_Delhi": [
    #     "Category:National Gallery of Modern Art, New Delhi",
    #     "Category:NGMA New Delhi"
    # ],
    # "District_Museum_Imphal": [
    #     "Category:District Museum, Imphal",
    #     "Category:Imphal District Museum"
    # ],
    # "Kannur_Archaeological_Museum": [
    #     "Category:Kannur Archaeological Museum",
    #     "Category:Kannur Museum"
    # ],
    # "Anantapur_Museum": [
    #     "Category:Anantapur Museum",
    #     "Category:Anantapur District Museum"
    # ],
    # "Maharaja_Sawai_Man_Singh_II_Museum_Jaipur": [
    #     "Category:Maharaja Sawai Man Singh II Museum",
    #     "Category:Sawai Man Singh Museum Jaipur"
    # ],
    # "Pune_Tribal_Museum": [
    #     "Category:Pune Tribal Museum",
    #     "Category:Tribal Museum Pune"
    # ],
    # "Heritage_Transport_Museum_Gurgaon": [
    #     "Category:Heritage Transport Museum",
    #     "Category:Heritage Transport Museum, Gurugram"
    # ],
    # "Nehru_Science_Centre_Mumbai": [
    #     "Category:Nehru Science Centre",
    #     "Category:Nehru Science Centre, Mumbai"
    # ],
    # # "Science_and_Technology_Museum_Patna": [
    # #     "Category:Science and Technology Museum, Patna",
    # #     "Category:Patna Science Museum"
    # # ],
    # # "State_Museum_Shimla": [
    # #     "Category:State Museum, Shimla",
    # #     "Category:Shimla State Museum"
    # # ]
    #    # Delhi / New Delhi specific — use the real Crafts Museum category, etc.
    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi": [
    #     "Category:Crafts Museum, New Delhi"
    # ],
    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi_2": [
    #     "Category:Crafts Museum, New Delhi"
    # ],
    # "National_Philatelic_Museum_New_Delhi": [
    #     "Category:Philately of India",          # stamp-related images
    #     "Category:Museums in India"
    # ],
    # "National_Philatelic_Museum_New_Delhi_2": [
    #     "Category:Philately of India",
    #     "Category:Museums in India"
    # ],
    # "National_Handicrafts_and_Handlooms_Museum_New_Delhi": [
    #     "Category:Crafts Museum, New Delhi"
    # ],

    # # NGMA already works but manual entry is fine:
    # "National_Gallery_of_Modern_Art_New_Delhi": [
    #     "Category:National Gallery of Modern Art, New Delhi"
    # ],

    # # Aviation / transport
    # "India_Civil_Aviation_Heritage_Museum_Delhi": [
    #     "Category:Indian aviation",
    #     "Category:Museums in India"
    # ],
    # "India_Civil_Aviation_Heritage_Museum": [
    #     "Category:Indian aviation",
    #     "Category:Museums in India"
    # ],
    # "Museum_of_Indian_Railways": [
    #     "Category:National Rail Museum, New Delhi",
    #     "Category:Railway museums in India"
    # ],
    # "Heritage_Transport_Museum_Gurgaon": [
    #     "Category:Transport museums in India",
    #     "Category:Museums in India"
    # ],

    # # Amdavad ni Gufa, Museum of Goa, Gujarat Science City, etc.
    # "Amdavad_ni_Gufa_Museum": [
    #     "Category:Amdavad ni Gufa",
    #     "Category:Museums in India"
    # ],
    # "Museum_of_Goa": [
    #     "Category:Museum of Goa (MOG)",
    #     "Category:Museums in India"
    # ],
    # "Gujarat_Science_City": [
    #     "Category:Gujarat Science City"
    # ],

    # # Manipur State Museum
    # "Manipur_State_Museum": [
    #     "Category:Manipur State Museum",
    #     "Category:Museums in India"
    # ],

    # # Sardar Vallabhbhai Patel Museum (Surat / Ahmedabad variants)
    # "Sardar_Vallabhbhai_Patel_Museum_Surat": [
    #     "Category:Museums in India"
    # ],
    # "Sardar_Vallabhbhai_Patel_Museum": [
    #     "Category:Museums in India"
    # ],

    # # Museum of Folk and Tribal Art (Delhi/Gurgaon style one)
    # "Museum_of_Folk_and_Tribal_Art_Delhi": [
    #     "Category:Museums in India"
    # ]
    #  "Sangrur_Museum": [
    #     "Category:Sangrur Museum",
    #     "Category:Sangrur District Museum"
    # ],
    # "Palace_Museum_Gangtok": [
    #     "Category:Palace Museum, Gangtok",
    #     "Category:Palace Museum Gangtok"
    # ],
    # "Ethnographic_Museum_Shillong": [
    #     "Category:Ethnographic Museum, Shillong",
    #     "Category:Ethnographic Museum Shillong"
    # ],
    # "Lok_Virsa_Museum_New_Delhi": [
    #     "Category:Lok Virsa Museum",
    #     "Category:Lok Virsa Museum, New Delhi"
    # ],
    # "Government_Museum_Baroda": [
    #     "Category:Government Museum, Baroda",
    #     "Category:Vadodara Government Museum"
    # ],
    # "District_Museum_Dibrugarh": [
    #     "Category:District Museum, Dibrugarh",
    #     "Category:Dibrugarh District Museum"
    # ],
    # "Museum_of_Religious_Arts_Varanasi": [
    #     "Category:Museum of Religious Arts",
    #     "Category:Museum of Religious Arts, Varanasi"
    # ],
    # "Government_Museum_Thanjavur": [
    #     "Category:Government Museum, Thanjavur",
    #     "Category:Thanjavur Government Museum"
    # ],
    # "Kerala_Museum_of_Folk_Art_Kochi": [
    #     "Category:Kerala Museum of Folk Art",
    #     "Category:Kerala Folk Art Museum Kochi"
    # ],
    # "Sanket_Heritage_Museum_Mysuru": [
    #     "Category:Sanket Heritage Museum",
    #     "Category:Sanket Heritage Museum Mysuru"
    # ],
    # "Victoria_Memorial_Kolkata": [
    #     "Category:Victoria Memorial, Kolkata",
    #     "Category:Victoria Memorial"
    # ],
    # "Museum_of_Punjab_Heritage_Ludhiana": [
    #     "Category:Museum of Punjab Heritage",
    #     "Category:Punjab Heritage Museum Ludhiana"
    # ],
    # "Railway_Heritage_Centre_Chennai": [
    #     "Category:Railway Heritage Centre, Chennai",
    #     "Category:Railway Heritage Centre Chennai"
    # ],
    # "Government_Museum_Ahmedabad": [
    #     "Category:Government Museum, Ahmedabad",
    #     "Category:Central Museum Ahmedabad"
    # ],
    # "Museum_of_Gujarat_History_Ahmedabad": [
    #     "Category:Museum of Gujarat History",
    #     "Category:Gujarat History Museum Ahmedabad"
    # ],
    # "Bikaner_Museum": [
    #     "Category:Bikaner Museum",
    #     "Category:Bikaner State Museum"
    # ],
    # "Gujarat_Maritime_Museum_Ahmedabad": [
    #     "Category:Gujarat Maritime Museum",
    #     "Category:Gujarat Maritime Museum, Ahmedabad"
    # ],
    # "Museum_of_National_Defence_New_Delhi": [
    #     "Category:Museum of National Defence",
    #     "Category:National Defence Museum, New Delhi"
    # ],
    # "Museum_of_Indian_Independence_New_Delhi": [
    #     "Category:Museum of Indian Independence",
    #     "Category:Independence Museum New Delhi"
    # ],
    # "Museum_of_Ancient_History_Patna": [
    #     "Category:Museum of Ancient History",
    #     "Category:Ancient History Museum Patna"
    # ],
    # "State_Tribal_Museum_Raipur": [
    #     "Category:State Tribal Museum, Raipur",
    #     "Category:State Tribal Museum Raipur"
    # ],
    # "Museum_of_Indian_Railways_Delhi": [
    #     "Category:Museum of Indian Railways",
    #     "Category:Indian Railways Museum New Delhi"
    # ],
    # "Museum_of_Indian_Culture_New_Delhi": [
    #     "Category:Museum of Indian Culture",
    #     "Category:Indian Culture Museum New Delhi"
    # ],
    # "Regional_Science_Centre_Bhubaneswar": [
    #     "Category:Regional Science Centre, Bhubaneswar",
    #     "Category:Regional Science Centre Bhubaneswar"
    # ],
    # "Museum_of_Indian_Art_New_Delhi": [
    #     "Category:Museum of Indian Art",
    #     "Category:Indian Art Museum New Delhi"
    # ],
    # "Heritage_Museum_Ranchi": [
    #     "Category:Heritage Museum, Ranchi",
    #     "Category:Ranchi Heritage Museum"
    # ],
    # "Museum_of_Tribal_Culture_Ranchi": [
    #     "Category:Museum of Tribal Culture",
    #     "Category:Tribal Culture Museum Ranchi"
    # ],
    # "Museum_of_Science_and_Technology_Bhopal": [
    #     "Category:Museum of Science & Technology, Bhopal",
    #     "Category:Science and Technology Museum Bhopal"
    # ],
    # "Museum_of_Central_Asian_and_Kargil_Trade_Artefacts_Kargil": [
    #     "Category:Museum of Central Asian and Kargil Trade Artefacts",
    #     "Category:Kargil Trade Museum"
    # ],
    # "Museum_of_Kashmir_Arts_Srinagar": [
    #     "Category:Museum of Kashmir Arts",
    #     "Category:Museum of Kashmir Arts, Srinagar"
    # ],
    # "Museum_of_Handicrafts_Jaipur": [
    #     "Category:Museum of Handicrafts",
    #     "Category:Handicrafts Museum Jaipur"
    # ],
    # "Museum_of_Indian_Textiles_New_Delhi": [
    #     "Category:Museum of Indian Textiles",
    #     "Category:Textile Museum New Delhi"
    # ],
    # "Museum_of_Folk_Arts_Shillong": [
    #     "Category:Museum of Folk Arts",
    #     "Category:Folk Arts Museum Shillong"
    # ],
    # "Museum_of_Archaeology_and_Ethnology_Guwahati": [
    #     "Category:Museum of Archaeology and Ethnology",
    #     "Category:Archaeology and Ethnology Museum Guwahati"
    # ],
    #   "Rajasthan_Textile_Museum_Jodhpur": [
    #     "Category:Rajasthan Textile Museum",
    #     "Category:Textile Museum Jodhpur"
    # ],
    # "Coorg_Heritage_Museum_Madikeri": [
    #     "Category:Coorg Heritage Museum",
    #     "Category:Coorg Heritage Museum Madikeri"
    # ],
    # "Bengal_Maritime_Museum_Howrah": [
    #     "Category:Bengal Maritime Museum",
    #     "Category:Bengal Maritime Museum Howrah"
    # ],
    # "Sikkim_Himalayan_Art_Museum_Gangtok": [
    #     "Category:Sikkim Himalayan Art Museum",
    #     "Category:Sikkim Himalayan Art Museum Gangtok"
    # ],
    # "Mizoram_Tribal_Heritage_Centre_Aizawl": [
    #     "Category:Mizoram Tribal Heritage Centre",
    #     "Category:Mizoram Tribal Heritage Centre Aizawl"
    # ],
    # "Chhattisgarh_Tribal_Museum_Raipur": [
    #     "Category:Chhattisgarh Tribal Museum",
    #     "Category:Tribal Museum Raipur"
    # ],
    # "Assam_Silk_Museum_Guwahati": [
    #     "Category:Assam Silk Museum",
    #     "Category:Silk Museum Guwahati"
    # ],
    # "Nagaland_War_Memorial_Museum_Kohima": [
    #     "Category:Nagaland War Memorial Museum",
    #     "Category:Nagaland War Memorial Museum Kohima"
    # ],
    # "Kerala_Spice_Museum_Kochi": [
    #     "Category:Kerala Spice Museum",
    #     "Category:Spice Museum Kochi"
    # ],
    # "Uttaranchal_Folk_Arts_Museum_Dehradun": [
    #     "Category:Uttaranchal Folk Arts Museum",
    #     "Category:Folk Arts Museum Dehradun"
    # ],
    # "Tamil_Nadu_Handloom_Museum_Coimbatore": [
    #     "Category:Tamil Nadu Handloom Museum",
    #     "Category:Handloom Museum Coimbatore"
    # ],
    # "Odisha_Tribal_Heritage_Museum_Bhubaneswar": [
    #     "Category:Odisha Tribal & Folk Art Museum",
    #     "Category:Tribal Heritage Museum Bhubaneswar"
    # ],
    # "Goa_Archaeological_Museum_Panjim": [
    #     "Category:Goa Archaeological Museum",
    #     "Category:Archaeological Museum Panjim"
    # ],
    # "Haryana_Folk_Culture_Museum_Hisar": [
    #     "Category:Haryana Folk Culture Museum",
    #     "Category:Folk Culture Museum Hisar"
    # ],
    # "MP_Stone_Sculpture_Museum_Indore": [
    #     "Category:Madhya Pradesh Stone Sculpture Museum",
    #     "Category:Stone Sculpture Museum Indore"
    # ],
    # "Jharkhand_Tribal_Art_Gallery_Ranchi": [
    #     "Category:Jharkhand Tribal Art Gallery",
    #     "Category:Tribal Art Gallery Ranchi"
    # ]
    #    "Sangrur_Museum": [
    #     "Category:Sangrur",
    #     "Category:Museums in Punjab",
    #     "Category:Museums in India"
    # ],

    # "Palace_Museum_Gangtok": [
    #     "Category:Gangtok",
    #     "Category:Palaces in Sikkim",
    #     "Category:Museums in Sikkim"
    # ],

    # "Ethnographic_Museum_Shillong": [
    #     "Category:Ethnographic museums",
    #     "Category:Shillong",
    #     "Category:Museums in Meghalaya"
    # ],

    # "Lok_Virsa_Museum_New_Delhi": [
    #     "Category:Lok Virsa",
    #     "Category:Folk culture of India",
    #     "Category:Museums in Delhi"
    # ],

    # "Government_Museum_Baroda": [
    #     "Category:Vadodara",
    #     "Category:Government Museum, Vadodara",
    #     "Category:Museums in Gujarat"
    # ],

    # "District_Museum_Dibrugarh": [
    #     "Category:Dibrugarh",
    #     "Category:District museums in India",
    #     "Category:Museums in Assam"
    # ],

    # "Museum_of_Religious_Arts_Varanasi": [
    #     "Category:Varanasi",
    #     "Category:Religion in India",
    #     "Category:Museums in Uttar Pradesh"
    # ],

    # "Government_Museum_Thanjavur": [
    #     "Category:Thanjavur",
    #     "Category:Government Museum, Thanjavur",
    #     "Category:Museums in Tamil Nadu"
    # ],

    # "Kerala_Museum_of_Folk_Art_Kochi": [
    #     "Category:Folk art of Kerala",
    #     "Category:Kochi",
    #     "Category:Museums in Kerala"
    # ],

    # "Sanket_Heritage_Museum_Mysuru": [
    #     "Category:Mysore",
    #     "Category:Heritage museums in Karnataka",
    #     "Category:Museums in India"
    # ],

    # "Museum_of_Punjab_Heritage_Ludhiana": [
    #     "Category:Punjab Heritage Museum",
    #     "Category:Ludhiana",
    #     "Category:Museums in Punjab"
    # ],

    # "Railway_Heritage_Centre_Chennai": [
    #     "Category:Railway Heritage Centre, Chennai",
    #     "Category:Rail transport in India",
    #     "Category:Museums in Tamil Nadu"
    # ],

    # "Government_Museum_Ahmedabad": [
    #     "Category:Central Museum Ahmedabad",
    #     "Category:Ahmedabad",
    #     "Category:Museums in Gujarat"
    # ],

    # "Museum_of_Gujarat_History_Ahmedabad": [
    #     "Category:Gujarat",
    #     "Category:History museums in India",
    #     "Category:Museums in Ahmedabad"
    # ],

    # "Bikaner_Museum": [
    #     "Category:Bikaner",
    #     "Category:Museums in Rajasthan",
    #     "Category:History of Rajasthan"
    # ],

    # "Gujarat_Maritime_Museum_Ahmedabad": [
    #     "Category:Maritime museums in India",
    #     "Category:Ahmedabad",
    #     "Category:Gujarat"
    # ],

    # "Museum_of_National_Defence_New_Delhi": [
    #     "Category:National Defence Museum",
    #     "Category:Military history of India",
    #     "Category:Museums in Delhi"
    # ],

    # "Museum_of_Indian_Independence_New_Delhi": [
    #     "Category:Independence museums",
    #     "Category:Indian independence movement",
    #     "Category:Museums in Delhi"
    # ],

    # "Museum_of_Ancient_History_Patna": [
    #     "Category:Patna",
    #     "Category:Ancient history museums",
    #     "Category:Museums in Bihar"
    # ],

    # "State_Tribal_Museum_Raipur": [
    #     "Category:State Tribal Museum, Raipur",
    #     "Category:Tribal culture of Chhattisgarh",
    #     "Category:Museums in Chhattisgarh"
    # ],

    # "Museum_of_Indian_Railways_Delhi": [
    #     "Category:National Rail Museum, New Delhi",
    #     "Category:Railway museums in India",
    #     "Category:Rail transport in India"
    # ],

    # "Museum_of_Indian_Culture_New_Delhi": [
    #     "Category:Indian culture",
    #     "Category:Museums in Delhi",
    #     "Category:Culture of India"
    # ],

    # "Regional_Science_Centre_Bhubaneswar": [
    #     "Category:Regional Science Centre, Bhubaneswar",
    #     "Category:Science museums in India",
    #     "Category:Bhubaneswar"
    # ],

    # "Museum_of_Indian_Art_New_Delhi": [
    #     "Category:Indian art",
    #     "Category:Art museums and galleries in India",
    #     "Category:Museums in Delhi"
    # ],

    # "Heritage_Museum_Ranchi": [
    #     "Category:Ranchi",
    #     "Category:Heritage museums in India",
    #     "Category:Museums in Jharkhand"
    # ],

    # "Museum_of_Tribal_Culture_Ranchi": [
    #     "Category:Tribal culture of Jharkhand",
    #     "Category:Ranchi",
    #     "Category:Tribal museums in India"
    # ],

    # "Museum_of_Science_and_Technology_Bhopal": [
    #     "Category:Science museums in India",
    #     "Category:Bhopal",
    #     "Category:Museums in Madhya Pradesh"
    # ],

    # "Museum_of_Central_Asian_and_Kargil_Trade_Artefacts_Kargil": [
    #     "Category:Kargil",
    #     "Category:Central Asian trade",
    #     "Category:Museums in Ladakh"
    # ],

    # "Museum_of_Kashmir_Arts_Srinagar": [
    #     "Category:Art of Jammu and Kashmir",
    #     "Category:Srinagar",
    #     "Category:Museums in Jammu and Kashmir"
    # ],

    # "Museum_of_Handicrafts_Jaipur": [
    #     "Category:Handicrafts of India",
    #     "Category:Jaipur",
    #     "Category:Museums in Rajasthan"
    # ],

    # "Museum_of_Indian_Textiles_New_Delhi": [
    #     "Category:Textiles of India",
    #     "Category:Textile museums in India",
    #     "Category:Museums in Delhi"
    # ],

    # "Museum_of_Folk_Arts_Shillong": [
    #     "Category:Folk arts of Meghalaya",
    #     "Category:Shillong",
    #     "Category:Museums in Meghalaya"
    # ],

    # "Museum_of_Archaeology_and_Ethnology_Guwahati": [
    #     "Category:Archaeology of Assam",
    #     "Category:Guwahati",
    #     "Category:Museums in Assam"
    # ],

    # "Rajasthan_Textile_Museum_Jodhpur": [
    #     "Category:Textiles of India",
    #     "Category:Jodhpur",
    #     "Category:Museums in Rajasthan"
    # ],

    # "Coorg_Heritage_Museum_Madikeri": [
    #     "Category:Coorg",
    #     "Category:Heritage museums in Karnataka",
    #     "Category:Museums in Kodagu"
    # ],

    # "Bengal_Maritime_Museum_Howrah": [
    #     "Category:Maritime museums in India",
    #     "Category:Howrah",
    #     "Category:Museums in West Bengal"
    # ],

    # "Sikkim_Himalayan_Art_Museum_Gangtok": [
    #     "Category:Himalayan art",
    #     "Category:Gangtok",
    #     "Category:Museums in Sikkim"
    # ],

    # "Mizoram_Tribal_Heritage_Centre_Aizawl": [
    #     "Category:Tribal culture of Mizoram",
    #     "Category:Aizawl",
    #     "Category:Museums in Mizoram"
    # ],

    # "Chhattisgarh_Tribal_Museum_Raipur": [
    #     "Category:Tribal museums in India",
    #     "Category:Raipur",
    #     "Category:Museums in Chhattisgarh"
    # ],

    # "Assam_Silk_Museum_Guwahati": [
    #     "Category:Silk",
    #     "Category:Guwahati",
    #     "Category:Textile museums in India"
    # ],

    # "Nagaland_War_Memorial_Museum_Kohima": [
    #     "Category:Kohima",
    #     "Category:War memorials in India",
    #     "Category:Museums in Nagaland"
    # ],

    # "Kerala_Spice_Museum_Kochi": [
    #     "Category:Spices of India",
    #     "Category:Kochi",
    #     "Category:Museums in Kerala"
    # ],

    # "Uttaranchal_Folk_Arts_Museum_Dehradun": [
    #     "Category:Folk arts of Uttarakhand",
    #     "Category:Dehradun",
    #     "Category:Museums in Uttarakhand"
    # ],

    # "Tamil_Nadu_Handloom_Museum_Coimbatore": [
    #     "Category:Handloom weaving",
    #     "Category:Coimbatore",
    #     "Category:Textile museums in India"
    # ],

    # "Odisha_Tribal_Heritage_Museum_Bhubaneswar": [
    #     "Category:Tribal culture of Odisha",
    #     "Category:Bhubaneswar",
    #     "Category:Museums in Odisha"
    # ],

    # "Haryana_Folk_Culture_Museum_Hisar": [
    #     "Category:Folk arts of Haryana",
    #     "Category:Hisar",
    #     "Category:Museums in Haryana"
    # ],

    # "MP_Stone_Sculpture_Museum_Indore": [
    #     "Category:Stone sculptures in India",
    #     "Category:Indore",
    #     "Category:Madhya Pradesh art"
    # ],

    # "Jharkhand_Tribal_Art_Gallery_Ranchi": [
    #     "Category:Tribal art of Jharkhand",
    #     "Category:Ranchi",
    #     "Category:Museums in Jharkhand"
    # ]
    #  "Bihar_Archaeological_Museum_Patna": [
    #     "Category:Bihar Archaeological Museum",
    #     "Category:Archaeological Museum Patna"
    # ],
    # "Punjab_Rural_Heritage_Museum_Ludhiana": [
    #     "Category:Punjab Rural Heritage Museum",
    #     "Category:Punjab Rural Heritage Museum Ludhiana"
    # ],
    # "West_Bengal_Folk_Museum_Darjeeling": [
    #     "Category:West Bengal Folk Museum",
    #     "Category:Folk Museum Darjeeling"
    # ],
    # "Karnataka_Palm_Leaf_Manuscript_Museum_Mysore": [
    #     "Category:Karnataka Palm Leaf Manuscript Museum",
    #     "Category:Palm Leaf Manuscript Museum Mysore"
    # ],
    # "Tripura_Royal_Heritage_Museum_Agartala": [
    #     "Category:Tripura Royal Heritage Museum",
    #     "Category:Royal Heritage Museum Agartala"
    # ],
    # "Maharashtra_Sculpture_Museum_Nagpur": [
    #     "Category:Maharashtra Sculpture Museum",
    #     "Category:Sculpture Museum Nagpur"
    # ],
    # "Andhra_Pradesh_Temple_Art_Museum_Visakhapatnam": [
    #     "Category:Andhra Pradesh Temple Art Museum",
    #     "Category:Temple Art Museum Visakhapatnam"
    # ],
    # "Uttarakhand_Himalayan_Culture_Museum_Nainital": [
    #     "Category:Uttarakhand Himalayan Culture Museum",
    #     "Category:Himalayan Culture Museum Nainital"
    # ],
    # "Tamil_Nadu_Bronze_Museum_Thanjavur": [
    #     "Category:Tamil Nadu Bronze Museum",
    #     "Category:Bronze Museum Thanjavur"
    # ],
    # "Rajasthan_Puppet_Museum_Udaipur": [
    #     "Category:Rajasthan Puppet Museum",
    #     "Category:Puppet Museum Udaipur"
    # ],
    # "Kerala_Boat_Museum_Kollam": [
    #     "Category:Kerala Boat Museum",
    #     "Category:Boat Museum Kollam"
    # ],
    # "Assam_Tea_Heritage_Museum_Jorhat": [
    #     "Category:Assam Tea Heritage Museum",
    #     "Category:Tea Heritage Museum Jorhat"
    # ],
    # "Manipur_Tribal_Dance_Museum_Imphal": [
    #     "Category:Manipur Tribal Dance Museum",
    #     "Category:Tribal Dance Museum Imphal"
    # ],
    # "Nagaland_Bamboo_Art_Museum_Wokha": [
    #     "Category:Nagaland Bamboo Art Museum",
    #     "Category:Bamboo Art Museum Wokha"
    # ],
    # "West_Bengal_Colonial_History_Museum_Kolkata": [
    #     "Category:West Bengal Colonial History Museum",
    #     "Category:Colonial History Museum Kolkata"
    # ],
    # "Goa_Shipwreck_Archaeology_Museum_Panjim": [
    #     "Category:Goa Shipwreck Archaeology Museum",
    #     "Category:Shipwreck Archaeology Museum Panjim"
    # ],
    # "Chhattisgarh_Handicraft_Museum_Bilaspur": [
    #     "Category:Chhattisgarh Handicraft Museum",
    #     "Category:Handicraft Museum Bilaspur"
    # ],
    # "MP_War_Museum_Indore": [
    #     "Category:Madhya Pradesh War Museum",
    #     "Category:War Museum Indore"
    # ],
    # "Bihar_Folk_Art_Museum_Muzaffarpur": [
    #     "Category:Bihar Folk Art Museum",
    #     "Category:Folk Art Museum Muzaffarpur"
    # ],
    # "Punjab_Sikh_Heritage_Museum_Amritsar": [
    #     "Category:Punjab Sikh Heritage Museum",
    #     "Category:Sikh Heritage Museum Amritsar"
    # ],
    # "Tripura_Tribal_Handloom_Museum_Agartala": [
    #     "Category:Tripura Tribal Handloom Museum",
    #     "Category:Tribal Handloom Museum Agartala"
    # ],
    # "Tamil_Nadu_Temple_Sculpture_Museum_Madurai": [
    #     "Category:Tamil Nadu Temple Sculpture Museum",
    #     "Category:Temple Sculpture Museum Madurai"
    # ],
    # "Uttarakhand_Natural_History_Museum_Dehradun": [
    #     "Category:Uttarakhand Natural History Museum",
    #     "Category:Natural History Museum Dehradun"
    # ],
    # "Karnataka_Mysore_Paintings_Museum_Mysore": [
    #     "Category:Karnataka Mysore Paintings Museum",
    #     "Category:Mysore Paintings Museum"
    # ],
    # "Rajasthan_Desert_Culture_Museum_Jaisalmer": [
    #     "Category:Rajasthan Desert Culture Museum",
    #     "Category:Desert Culture Museum Jaisalmer"
    # ],
    # "Kerala_Elephant_Heritage_Museum_Thrissur": [
    #     "Category:Kerala Elephant Heritage Museum",
    #     "Category:Elephant Heritage Museum Thrissur"
    # ],
    # "Mizoram_Traditional_Dress_Museum_Aizawl": [
    #     "Category:Mizoram Traditional Dress Museum",
    #     "Category:Traditional Dress Museum Aizawl"
    # ],
    # "Andhra_Pradesh_Colonial_History_Museum_Vijayawada": [
    #     "Category:Andhra Pradesh Colonial History Museum",
    #     "Category:Colonial History Museum Vijayawada"
    # ],
    # "Assam_Tribal_Music_Museum_Dispur": [
    #     "Category:Assam Tribal Music Museum",
    #     "Category:Tribal Music Museum Dispur"
    # ],
    # "Nagaland_War_History_Museum_Dimapur": [
    #     "Category:Nagaland War History Museum",
    #     "Category:War History Museum Dimapur"
    # ],
    # "Bihar_Buddhist_Heritage_Museum_Patna": [
    #     "Category:Bihar Buddhist Heritage Museum",
    #     "Category:Buddhist Heritage Museum Patna"
    # ],
    # "Punjab_Rural_Arts_Museum_Fatehgarh_Sahib": [
    #     "Category:Punjab Rural Arts Museum",
    #     "Category:Rural Arts Museum Fatehgarh Sahib"
    # ],
    # "Goa_Church_Art_Museum_Panjim": [
    #     "Category:Goa Church Art Museum",
    #     "Category:Church Art Museum Panjim"
    # ],
    # "MP_Tribal_Jewellery_Museum_Bhopal": [
    #     "Category:Madhya Pradesh Tribal Jewellery Museum",
    #     "Category:Tribal Jewellery Museum Bhopal"
    # ],
    # "Tripura_Royal_Armory_Museum_Agartala": [
    #     "Category:Tripura Royal Armory Museum",
    #     "Category:Royal Armory Museum Agartala"
    # ],
    # "Uttarakhand_Himalayan_Natural_History_Museum_Rishikesh": [
    #     "Category:Uttarakhand Himalayan Natural History Museum",
    #     "Category:Himalayan Natural History Museum Rishikesh"
    # ],
    # "Kerala_Kathakali_Museum_Kochi": [
    #     "Category:Kerala Kathakali Museum",
    #     "Category:Kathakali Museum Kochi"
    # ],
    # "Karnataka_Mysore_Royal_Art_Museum_Mysore": [
    #     "Category:Karnataka Mysore Royal Art Museum",
    #     "Category:Mysore Royal Art Museum"
    # ],
    # "Tamil_Nadu_Bronze_Sculpture_Museum_Chennai": [
    #     "Category:Tamil Nadu Bronze Sculpture Museum",
    #     "Category:Bronze Sculpture Museum Chennai"
    # ],
    # "Rajasthan_Camel_Heritage_Museum_Bikaner": [
    #     "Category:Rajasthan Camel Heritage Museum",
    #     "Category:Camel Heritage Museum Bikaner"
    # ],
    # "West_Bengal_Tribal_Art_Museum_Darjeeling": [
    #     "Category:West Bengal Tribal Art Museum",
    #     "Category:Tribal Art Museum Darjeeling"
    # ],
    # "Assam_Tea_Plantation_Museum_Jorhat": [
    #     "Category:Assam Tea Plantation Museum",
    #     "Category:Tea Plantation Museum Jorhat"
    # ],
    # "Nagaland_Cultural_History_Museum_Kohima": [
    #     "Category:Nagaland Cultural History Museum",
    #     "Category:Cultural History Museum Kohima"
    # ],
    # "Goa_Portuguese_Heritage_Museum_Panjim": [
    #     "Category:Goa Portuguese Heritage Museum",
    #     "Category:Portuguese Heritage Museum Panjim"
    # ],
    # "Chhattisgarh_Folk_Arts_Museum_Raipur": [
    #     "Category:Chhattisgarh Folk Arts Museum",
    #     "Category:Folk Arts Museum Raipur"
    # ],
    #  "Rajasthan_Textile_Museum_Jodhpur": [
    #     "Category:Textiles of Rajasthan",
    #     "Category:Jodhpur Museums"
    # ],
    # "Kerala_Spice_Museum_Kochi": [
    #     "Category:Spices",
    #     "Category:Museums in Kochi"
    # ],
    # "Goa_Archaeological_Museum_Panjim": [
    #     "Category:Archaeological Museum (Goa)",
    #     "Category:Museums in Goa"
    # ],
    # "West_Bengal_Colonial_History_Museum_Kolkata": [
    #     "Category:History of Kolkata",
    #     "Category:Museums in Kolkata"
    # ],
    # "Tamil_Nadu_Bronze_Museum_Thanjavur": [
    #     "Category:Bronze sculptures of Tamil Nadu",
    #     "Category:Museums in Thanjavur"
    # ],
    # "Rajasthan_Puppet_Museum_Udaipur": [
    #     "Category:Arts in Udaipur",
    #     "Category:Puppetry in Rajasthan"
    # ],
    # "Kerala_Boat_Museum_Kollam": [
    #     "Category:Boats of Kerala",
    #     "Category:Museums in Kerala"
    # ],
    # "Assam_Tea_Heritage_Museum_Jorhat": [
    #     "Category:Tea industry in Assam",
    #     "Category:Museums in Assam"
    # ],
    # "Nagaland_Bamboo_Art_Museum_Wokha": [
    #     "Category:Bamboo art",
    #     "Category:Museums in Nagaland"
    # ],
    # "Tripura_Royal_Heritage_Museum_Agartala": [
    #     "Category:Agartala",
    #     "Category:Culture of Tripura"
    # ]
    # "Bihar_Archaeological_Museum_Patna": [
    #     "Category:Archaeological Survey of India",
    #     "Category:Patna"
    # ],
    # "Punjab_Rural_Heritage_Museum_Ludhiana": [
    #     "Category:Ludhiana",
    #     "Category:Rural culture of India"
    # ],
    # "West_Bengal_Folk_Museum_Darjeeling": [
    #     "Category:Darjeeling",
    #     "Category:Folk art of India"
    # ],
    # "Karnataka_Palm_Leaf_Manuscript_Museum_Mysore": [
    #     "Category:Palm leaf manuscripts",
    #     "Category:Mysore"
    # ],
    # "Maharashtra_Sculpture_Museum_Nagpur": [
    #     "Category:Nagpur",
    #     "Category:Sculptures in India"
    # ],
    # "Andhra_Pradesh_Temple_Art_Museum_Visakhapatnam": [
    #     "Category:Visakhapatnam",
    #     "Category:Hindu temple art"
    # ],
    # "Uttarakhand_Himalayan_Culture_Museum_Nainital": [
    #     "Category:Nainital",
    #     "Category:Himalayan culture"
    # ],
    # "Tamil_Nadu_Bronze_Museum_Thanjavur": [
    #     "Category:Bronze sculptures of Tamil Nadu",
    #     "Category:Thanjavur"
    # ],
    # "Rajasthan_Puppet_Museum_Udaipur": [
    #     "Category:Puppetry in Rajasthan",
    #     "Category:Udaipur"
    # ],
    # "Manipur_Tribal_Dance_Museum_Imphal": [
    #     "Category:Imphal",
    #     "Category:Tribal dances of India"
    # ],
    # "Nagaland_Bamboo_Art_Museum_Wokha": [
    #     "Category:Wokha district",
    #     "Category:Bamboo crafts"
    # ],
    # "Goa_Shipwreck_Archaeology_Museum_Panjim": [
    #     "Category:Shipwrecks of India",
    #     "Category:Panjim"
    # ],
    # "Chhattisgarh_Handicraft_Museum_Bilaspur": [
    #     "Category:Bilaspur district, Chhattisgarh",
    #     "Category:Handicrafts of India"
    # ],
    # "MP_War_Museum_Indore": [
    #     "Category:Indore",
    #     "Category:War memorials in India"
    # ],
    # "Bihar_Folk_Art_Museum_Muzaffarpur": [
    #     "Category:Muzaffarpur",
    #     "Category:Folk art of India"
    # ],
    # "Punjab_Sikh_Heritage_Museum_Amritsar": [
    #     "Category:Amritsar",
    #     "Category:Sikh culture"
    # ],
    # "Tripura_Tribal_Handloom_Museum_Agartala": [
    #     "Category:Agartala",
    #     "Category:Handloom industry in India"
    # ],
    # "Tamil_Nadu_Temple_Sculpture_Museum_Madurai": [
    #     "Category:Madurai",
    #     "Category:Hindu temple sculpture"
    # ],
    # "Uttarakhand_Natural_History_Museum_Dehradun": [
    #     "Category:Dehradun",
    #     "Category:Natural history museums in India"
    # ],
    # "Karnataka_Mysore_Paintings_Museum_Mysore": [
    #     "Category:Mysore painting",
    #     "Category:Mysore"
    # ]
    # "National_Museum_New_Delhi": [
    #     "Category:National Museum, New Delhi",
    #     "Category:Interiors of National Museum, New Delhi"
    # ],
    # "National_Gallery_of_Modern_Art_New_Delhi": [
    #     "Category:National Gallery of Modern Art, New Delhi"
    # ],
    # "Bharat_Kala_Bhavan_Varanasi": [
    #     "Category:Bharat Kala Bhavan"
    # ],
    # "Salar_Jung_Museum_Hyderabad": [
    #     "Category:Salar Jung Museum",
    #     "Category:Interiors of Salar Jung Museum"
    # ],
    # "Bihar_Museum_Patna": [
    #     "Category:Bihar Museum"
    # ],
    # "Victoria_Memorial_Kolkata": [
    #     "Category:Victoria Memorial, Kolkata",
    #     "Category:Interior of Victoria Memorial"
    # ],
    # "Indian_Museum_Kolkata": [
    #     "Category:Indian Museum, Kolkata",
    #     "Category:Interiors of Indian Museum"
    # ],
    # "Allahabad_Museum": [
    #     "Category:Allahabad Museum"
    # ],
    # "Government_Museum_Egmore_Chennai": [
    #     "Category:Government Museum, Chennai",
    #     "Category:Interiors of the Government Museum Chennai"
    # ],
    # "Chhatrapati_Shivaji_Maharaj_Vastu_Sangrahalaya_Mumbai": [
    #     "Category:Prince of Wales Museum, Mumbai",
    #     "Category:Interiors of Chhatrapati Shivaji Maharaj Vastu Sangrahalaya"
    # ],
    # "Manipur_State_Museum": [
    #     "Category:Manipur State Museum"
    # ],
    # "National_Rail_Museum_New_Delhi": [
    #     "Category:National Rail Museum, New Delhi"
    # ],
    # "Rail_Museum_Mysore": [
    #     "Category:Rail Museum, Mysuru"
    # ],
    # "Gwalior_Fort_Museum": [
    #     "Category:Gwalior Fort Museum"
    # ],
    # "Khajuraho_Archaeological_Museum": [
    #     "Category:Khajuraho Archaeological Museum"
    # ],
    # "Archaeological_Museum_Hampi": [
    #     "Category:Archaeological Museum, Hampi"
    # ],
    # "Calico_Museum_of_Textiles_Ahmedabad": [
    #     "Category:Calico Museum of Textiles"
    # ],
    # "Napier_Museum_Thiruvananthapuram": [
    #     "Category:Napier Museum"
    # ],
    # "Gandhi_Smriti_New_Delhi": [
    #     "Category:Gandhi Smriti"
    # ],
    # "Indira_Gandhi_Memorial_Museum_New_Delhi": [
    #     "Category:Indira Gandhi Memorial Museum"
    # ],
    # # "Shankar's_International_Dolls_Museum_Delhi": [
    # #     "Category:Shankar's International Dolls Museum"
    # # ],
    # # "Lok_Kala_Mandal_Udaipur": [
    # #     "Category:Folk Art Museum, Udaipur"
    # # ],
    # # "Jawahar_Kala_Kendra_Jaipur": [
    # #     "Category:Jawahar Kala Kendra"
    # # ],
    # # "HAL_Heritage_Centre_and_Aerospace_Museum_Bangalore": [
    # #     "Category:HAL Aerospace Museum"
    # # ],
    # # "Regional_Science_Centre_Bhopal": [
    # #     "Category:Regional Science Centre, Bhopal"
    # # ],
    # # "Gujarat_Science_City": [
    # #     "Category:Gujarat Science City"
    # # ],
    # # "Sundarbans_Interpretation_Centre_Kolkata": [
    # #     "Category:Sundarbans Interpretation Centre"
    # # ]
    #    "Bharat_Kala_Bhavan_Varanasi": [
    #     "Category:Bharat Kala Bhavan, Varanasi"
    # ],

    # "Darjeeling_Himalayan_Railway_Museum_Darjeeling": [
    #     "Category:Darjeeling Himalayan Railway Museum, Darjeeling"
    # ],

    # "Assam_State_Museum_Guwahati": [
    #     "Category:Assam State Museum, Guwahati"
    # ],

    # "Chhattisgarh_State_Museum_Raipur": [
    #     "Category:Chhattisgarh State Museum, Raipur"
    # ],

    # "Wayanad_Heritage_Museum_Wayanad": [
    #     "Category:Wayanad Heritage Museum, Wayanad"
    # ],

    # "West_Bengal_Police_Museum_Kolkata": [
    #     "Category:West Bengal Police Museum, Kolkata"
    # ],

    # "Zoological_Museum_Kolkata": [
    #     "Category:Zoological Museum, Kolkata"
    # ],

    # "Vellore_Fort_Museum_Vellore": [
    #     "Category:Vellore Fort Museum, Vellore"
    # ],

    # "Vasai_Fort_Museum_Vasai": [
    #     "Category:Vasai Fort Museum, Vasai"
    # ],

    # "Coorg_Museum_Coorg": [
    #     "Category:Coorg Museum, Coorg"
    # ],

    # "Chamba_Museum_Chamba": [
    #     "Category:Chamba Museum, Chamba"
    # ],

    # "Aurangabad_Caves_Museum_Aurangabad": [
    #     "Category:Aurangabad Caves Museum, Aurangabad"
    # ],

    # "Archaeological_Museum_Bhopal": [
    #     "Category:Archaeological Museum, Bhopal"
    # ],

    # "Archaeological_Museum_Mathura": [
    #     "Category:Archaeological Museum, Mathura"
    # ],

    # "Bastar_Tribal_Museum_Bastar": [
    #     "Category:Bastar Tribal Museum, Bastar"
    # ],

    # "Bhilai_Steel_Plant_Museum_Bhilai": [
    #     "Category:Bhilai Steel Plant Museum, Bhilai"
    # ],

    # "Bhadrak_Museum_Bhadrak": [
    #     "Category:Bhadrak Museum, Bhadrak"
    # ],

    # "Bengal_Museum_of_Industrial_Archaeology_Kolkata": [
    #     "Category:Bengal Museum of Industrial Archaeology, Kolkata"
    # ],

    # "Balasore_Museum_Balasore": [
    #     "Category:Balasore Museum, Balasore"
    # ],

    # "Amravati_Archaeological_Museum_Amravati": [
    #     "Category:Amravati Archaeological Museum, Amravati"
    # ],

    # "Ambedkar_Memorial_Indore": [
    #     "Category:Ambedkar Memorial, Indore"
    # ],

    # "Alappuzha_Maritime_Museum_Alappuzha": [
    #     "Category:Alappuzha Maritime Museum, Alappuzha"
    # ],

    # "Acharya_Jagadish_Chandra_Bose_Indian_Botanical_Museum_Kolkata": [
    #     "Category:Acharya Jagadish Chandra Bose Indian Botanical Museum, Kolkata"
    # ],

    # "Darbhanga_Museum_Darbhanga": [
    #     "Category:Darbhanga Museum, Darbhanga"
    # ],

    # "Dehradun_Fossil_Museum_Dehradun": [
    #     "Category:Dehradun Fossil Museum, Dehradun"
    # ],

    # "Dharamshala_Museum_Dharamshala": [
    #     "Category:Dharamshala Museum, Dharamshala"
    # ],

    # "Gandhinagar_Science_Museum_Gandhinagar": [
    #     "Category:Gandhinagar Science Museum, Gandhinagar"
    # ],

    # "Gaya_Museum_Gaya": [
    #     "Category:Gaya Museum, Gaya"
    # ],

    # "Guntur_Museum_Guntur": [
    #     "Category:Guntur Museum, Guntur"
    # ],

    # "Haridwar_Museum_Haridwar": [
    #     "Category:Haridwar Museum, Haridwar"
    # ],

    # "Howrah_Museum_Howrah": [
    #     "Category:Howrah Museum, Howrah"
    # ],

    # "Indore_Museum_Indore": [
    #     "Category:Indore Museum, Indore"
    # ],

    # "Itanagar_State_Museum_Itanagar": [
    #     "Category:Itanagar State Museum, Itanagar"
    # ],

    # "Jaipur_City_Museum_Jaipur": [
    #     "Category:Jaipur City Museum, Jaipur"
    # ],

    # "Jhansi_Fort_Museum_Jhansi": [
    #     "Category:Jhansi Fort Museum, Jhansi"
    # ],

    # # "Kanyakumari_Museum_Kanyakumari": [
    # #     "Category:Kanyakumari Museum, Kanyakumari"
    # # ]
    #    "New_Delhi_Railway_Museum_New_Delhi": [
    #     "Category:National Rail Museum, New Delhi"
    # ],
    # "Assam_State_Museum_Guwahati": [
    #     "Category:Assam State Museum, Guwahati"
    # ],
    # "Aurangabad_Caves_Museum_Aurangabad": [
    #     "Category:Aurangabad Caves"
    # ],
    # "Darjeeling_Himalayan_Railway_Museum_Darjeeling": [
    #     "Category:Darjeeling Himalayan Railway Museum, Darjeeling"
    # ],
    # "Acharya_Jagadish_Chandra_Bose_Indian_Botanical_Museum_Kolkata": [
    #     "Category:Acharya Jagadish Chandra Bose Indian Botanical Museum, Kolkata"
    # ],
    # "Dehradun_Fossil_Museum_Dehradun": [
    #     "Category:Dehradun Fossil Museum, Dehradun"
    # ],
    # "Wayanad_Heritage_Museum_Wayanad": [
    #     "Category:Wayanad Heritage Museum, Wayanad"
    # ],
    # "Vellore_Fort_Museum_Vellore": [
    #     "Category:Vellore Fort Museum, Vellore"
    # ],
    # "Vasai_Fort_Museum_Vasai": [
    #     "Category:Vasai Fort Museum, Vasai"
    # ],
    # "Coorg_Museum_Coorg": [
    #     "Category:Coorg Museum, Coorg"
    # ],
    # "Chamba_Museum_Chamba": [
    #     "Category:Chamba Museum, Chamba"
    # ],
    # "Archaeological_Museum_Bhopal": [
    #     "Category:Archaeological Museum, Bhopal"
    # ],
    # "Archaeological_Museum_Mathura": [
    #     "Category:Archaeological Museum, Mathura"
    # ],
    # "Bastar_Tribal_Museum_Bastar": [
    #     "Category:Bastar Tribal Museum, Bastar"
    # ],
    # "Bhilai_Steel_Plant_Museum_Bhilai": [
    #     "Category:Bhilai Steel Plant Museum, Bhilai"
    # ],
    # "Bhadrak_Museum_Bhadrak": [
    #     "Category:Bhadrak Museum, Bhadrak"
    # ],
    # "Bengal_Museum_of_Industrial_Archaeology_Kolkata": [
    #     "Category:Bengal Museum of Industrial Archaeology, Kolkata"
    # ],
    # "Balasore_Museum_Balasore": [
    #     "Category:Balasore Museum, Balasore"
    # # ],
    # # "Ambedkar_Memorial_Indore": [
    # #     "Category:Ambedkar Memorial, Indore"
    # # ],
    # # "Indore_Museum_Indore": [
    # #     "Category:Indore Museum, Indore"
    # # ],
    # # "Itanagar_State_Museum_Itanagar": [
    # #     "Category:Itanagar State Museum, Itanagar"
    # # ],
    # # "Jaipur_City_Museum_Jaipur": [
    # #     "Category:Jaipur City Museum, Jaipur"
    # # ]
    # "Thanjavur_Archaeological_Museum_Thanjavur": [
    #     "Category:Thanjavur Art Gallery"
    # ],

    # "Thrissur_Museum_Thrissur": [
    #     "Category:Archaeological Museum, Thrissur"
    # ],

    # "Shimla_State_Museum_Shimla": [
    #     "Category:Shimla State Museum"
    # ],

    # "Orai_Museum_Orai": [
    #     # Has no dedicated museum category, but images exist under city category
    #     "Category:Orai"
    # ],

#     # "Palakkad_Museum_Palakkad": [
#     #     "Category:Palakkad"
#     # ],

#     # "Panchkula_Museum_Panchkula": [
#     #     "Category:Panchkula"
#     # ],
# "Darbhanga_Museum_Darbhanga": [
#         "Category:Darbhanga"
#     ],

#     "Dharamshala_Museum_Dharamshala": [
#         "Category:Dharamshala"
#     ],

#     "Aurangabad_Caves_Museum_Aurangabad": [
#         "Category:Aurangabad Caves"
#     ],

#     "Asansol_Museum_Asansol": [
#         "Category:Asansol"
#     ],

#     "Archaeological_Museum_Mathura": [
#         "Category:Government Museum, Mathura"
#     ],

#     "Archaeological_Museum_Bhopal": [
#         "Category:State Museum, Bhopal"
#     ],

#     "Almora_Museum_Almora": [
#         "Category:Almora"
#     ],

#     "Adilabad_Museum_Adilabad": [
#         "Category:Adilabad"
#     ],

#     "Aizawl_Museum_Aizawl": [
#         "Category:Aizawl"
#     ],

#     "Alappuzha_Maritime_Museum_Alappuzha": [
#         "Category:Alleppey"
#     ],

#     "Aligarh_Museum_Aligarh": [
#         "Category:Aligarh"
#     ],

#     "Anand_Museum_Anand": [
#         "Category:Anand"
#     ],

#     "Assam_State_Museum_Guwahati": [
#         "Category:Assam State Museum"
#     ],

#     "Bhilai_Steel_Plant_Museum_Bhilai": [
#         "Category:Bhilai Steel Plant"
#     ],

#     "Brahmapur_Museum_Brahmapur": [
#         "Category:Brahmapur"
#     ],

#     "Chakradharpur_Museum_Chakradharpur": [
#         "Category:Chakradharpur"
#     ],

#     "Chamba_Museum_Chamba": [
#         "Category:Chamba (Himachal Pradesh)"
#     ],

#     "Coorg_Museum_Coorg": [
#         "Category:Kodagu district"
#     ],

#     "Bankura_Museum_Bankura": [
#         "Category:Bankura"
#     ],

#     "Balasore_Museum_Balasore": [
#         "Category:Balasore"
#     ],

#     "Bastar_Tribal_Museum_Bastar": [
#         "Category:Bastar district"
#     ],

#     "Begum_Rokeya_Museum_Ranaghat": [
#         "Category:Ranaghat"
#     ],

#     "Darrang_Museum_Mangaldoi": [
#         "Category:Mangaldoi"
#     ],

#     "Bengal_Museum_of_Industrial_Archaeology_Kolkata": [
#         "Category:Kolkata"
#     ],

#     "Bhadrak_Museum_Bhadrak": [
#         "Category:Bhadrak"
#     ],

#     "Bhandara_Museum_Bhandara": [
#         "Category:Bhandara"
#     ],

#     "Chhattisgarh_State_Museum_Raipur": [
#         "Category:Raipur"
#     ],

#     "Coimbatore_Museum_Coimbatore": [
#         "Category:Coimbatore"
#     ],

#     "Dehradun_Fossil_Museum_Dehradun": [
#         "Category:Dehradun"
#     ],

#     "Gandhinagar_Science_Museum_Gandhinagar": [
#         "Category:Gandhinagar"
#     ],

#     "Vasai_Fort_Museum_Vasai": [
#         "Category:Vasai Fort"
#     ],

#     "Vellore_Fort_Museum_Vellore": [
#         "Category:Vellore Fort"
#     ],

#     "Veraval_Museum_Veraval": [
#         "Category:Veraval"
#     ],

#     "Vizianagaram_Museum_Vizianagaram": [
#         "Category:Vizianagaram"
#     ],

#     "West_Bengal_Police_Museum_Kolkata": [
#         "Category:West Bengal Police Museum"
#     ],

#     "Yamunanagar_Museum_Yamunanagar": [
#         "Category:Yamunanagar"
#     ],

#     "Zawar_Mines_Museum_Udaipur": [
#         "Category:Zawar mines"
#     ],
#     "Wayanad_Heritage_Museum_Wayanad": [
#         "Category:Wayanad Heritage Museum"
#     ],

#     "Zoological_Museum_Kolkata": [
#         "Category:Zoological Museum, Kolkata"
#     ],

#     "Panaji_Museum_Panaji": [
#         "Category:Panjim"
#     ],

#     "Pune_Museum_Pune": [
#         "Category:Pune"
#     ],

#     "Rajkot_Museum_Rajkot": [
#         "Category:Rajkot"
#     ],

#     "Rajnandgaon_Museum_Rajnandgaon": [
#         "Category:Rajnandgaon"
#     ],

#     "Raipur_Museum_Raipur": [
#         "Category:Raipur"
#     ],

#     "Rohtak_Museum_Rohtak": [
#         "Category:Rohtak"
#     ],

#     "Salem_Museum_Salem": [
#         "Category:Salem, Tamil Nadu"
#     ],

#     "Sambalpur_Museum_Sambalpur": [
#         "Category:Sambalpur"
#     ],

#     "Sangli_Museum_Sangli": [
#         "Category:Sangli"
#     ],

#     "Satara_Museum_Satara": [
#         "Category:Satara"
#     ],

#     "Shimla_State_Museum_Shimla": [
#         "Category:Shimla State Museum"
#     ],

#     "Siliguri_Museum_Siliguri": [
#         "Category:Siliguri"
#     ],

#     "Solapur_Museum_Solapur": [
#         "Category:Solapur"
#     ],

#     "Srinagar_Museum_Srinagar": [
#         "Category:Srinagar"
#     ],

#     "Thanjavur_Archaeological_Museum_Thanjavur": [
#         "Category:Thanjavur Archaeological Museum"
#     ],

#     "Thiruvananthapuram_Museum_Thiruvananthapuram": [
#         "Category:Thiruvananthapuram"
#     ],

#     "Thrissur_Museum_Thrissur": [
#         "Category:Thrissur"
#     ],

#     "Tiruchirappalli_Museum_Tiruchirappalli": [
#         "Category:Tiruchirappalli"
#     ],

#     "Tirunelveli_Museum_Tirunelveli": [
#         "Category:Tirunelveli"
#     ],

#     "Udupi_Museum_Udupi": [
#         "Category:Udupi"
#     ],

#     "Vadodara_Museum_Vadodara": [
#         "Category:Vadodara Museum & Picture Gallery"
#     ],

#     "Varanasi_Museum_Varanasi": [
#         "Category:Varanasi"
#     ],

#     "Vellore_Museum_Vellore": [
#         "Category:Vellore"
#     ],

#     "Vidisha_Museum_Vidisha": [
#         "Category:Vidisha"
#     ],

#     "Warangal_Museum_Warangal": [
#         "Category:Warangal Fort"
#     ],

#     "Acharya_Jagadish_Chandra_Bose_Indian_Botanical_Museum_Kolkata": [
#         "Category:Botanical Survey of India"
#     ],

#     "Assam_State_Museum_Guwahati": [
#         "Category:Assam State Museum"
#     ],

#     "Bhilai_Steel_Plant_Museum_Bhilai": [
#         "Category:Bhilai Steel Plant"
#     ],

#     "Chennai_Museum_Chennai": [
#         "Category:Chennai"
#     ],

#     "Chitradurga_Fort_Museum_Chitradurga": [
#         "Category:Chitradurga Fort"
#     ],

#     "Dhanbad_Museum_Dhanbad": [
#         "Category:Dhanbad"
#     ],

#     "Gandhinagar_Science_Museum_Gandhinagar": [
#         "Category:Gandhinagar"
#     ],

#     "Vasai_Fort_Museum_Vasai": [
#         "Category:Vasai Fort"
#     ],

#     "Veraval_Museum_Veraval": [
#         "Category:Veraval"
#     ],

#     "Yamunanagar_Museum_Yamunanagar": [
#         "Category:Yamunanagar"
#     ]

    # "Panaji_Museum_Panaji": [
    #     "Category:Panaji"
    # ],

    # "Raipur_Museum_Raipur": [
    #     "Category:Raipur"
    # ],

    # "Raurkela_Museum_Raurkela": [
    #     "Category:Rourkela"
    # ],

    # "Sambalpur_Museum_Sambalpur": [
    #     "Category:Sambalpur"
    # ],

    # "Silchar_Museum_Silchar": [
    #     "Category:Silchar"
    # ],

    # "Siliguri_Museum_Siliguri": [
    #     "Category:Siliguri"
    # ],

    # "Solapur_Museum_Solapur": [
    #     "Category:Solapur"
    # ],

    # "Tezpur_Museum_Tezpur": [
    #     "Category:Tezpur"
    # ],

    # "Udupi_Museum_Udupi": [
    #     "Category:Udupi"
    # ],

    # "Varanasi_Museum_Varanasi": [
    #     "Category:Varanasi"
    # ],

    # "Warangal_Museum_Warangal": [
    #     "Category:Warangal"
    # ],

    # "Wayanad_Heritage_Museum_Wayanad": [
    #     "Category:Wayanad Heritage Museum"
    # ],

    # "Zoological_Museum_Kolkata": [
    #     "Category:Zoological Museum, Kolkata"
    # ],

    # "Balangir_Museum_Balangir": [
    #     "Category:Balangir"
    # ],

    # "Barmer_Museum_Barmer": [
    #     "Category:Barmer"
    # ],

    # "Begusarai_Museum_Begusarai": [
    #     "Category:Begusarai"
    # ],

    # "Brahmapur_Museum_Brahmapur": [
    #     "Category:Brahmapur"
    # ],

    # "Chennai_Museum_Chennai": [
    #     "Category:Government Museum, Chennai"
    # ],

    # "Chitradurga_Fort_Museum_Chitradurga": [
    #     "Category:Chitradurga Fort"
    # ],

    # "Darrang_Museum_Mangaldoi": [
    #     "Category:Mangaldoi"
    # ],

    # "Dhanbad_Museum_Dhanbad": [
    #     "Category:Dhanbad"
    # ]
    #  "Shimla_State_Museum_Shimla": [
    #     "Category:Interior of the Shimla State Museum"
    # ],
    # "Thanjavur_Archaeological_Museum_Thanjavur": [
    #     "Category:Interior of the Thanjavur Archaeological Museum"
    # ],
    # "Thrissur_Museum_Thrissur": [
    #     "Category:Interior of the Thrissur Museum"
    # ],
    # "Zoological_Museum_Kolkata": [
    #     "Category:Interior of the Zoological Museum"
    # ],
    # "Assam_State_Museum_Guwahati": [
    #     "Category:Interior of the Assam State Museum"
    # ],
    # "Wayanad_Heritage_Museum_Wayanad": [
    #     "Category:Interior of the Wayanad Heritage Museum"
    # ],
    # "Vellore_Fort_Museum_Vellore": [
    #     "Category:Interior of the Vellore Fort Museum"
    # ],
    # "Bast ar_Tribal_Museum_Bastar": [
    #     "Category:Interior of the Bastar Tribal Museum"
    # ],
    # "Chamba_Museum_Chamba": [
    #     "Category:Interior of the Chamba Museum"
    # ],
    # "Darbhanga_Museum_Darbhanga": [
    #     "Category:Interior of the Darbhanga Museum"
    # ],
    # "Dharamshala_Museum_Dharamshala": [
    #     "Category:Interior of the Dharamshala Museum"
    # ],
    #   "Bankura_Museum_Bankura": [
    #     "Category:Interior of the Bankura Museum"
    # ],
    # "Balasore_Museum_Balasore": [
    #     "Category:Interior of the Balasore Museum"
    # ],
    # "Bhilai_Steel_Plant_Museum_Bhilai": [
    #     "Category:Interior of the Bhilai Steel Plant Museum"
    # ],
    # "Chennai_Museum_Chennai": [
    #     "Category:Interior of the Chennai Museum"
    # ],
    # "Coimbatore_Museum_Coimbatore": [
    #     "Category:Interior of the Coimbatore Museum"
    # ],
    # "Dehradun_Fossil_Museum_Dehradun": [
    #     "Category:Interior of the Dehradun Fossil Museum"
    # ],
    # "Gandhinagar_Science_Museum_Gandhinagar": [
    #     "Category:Interior of the Gandhinagar Science Museum"
    # ],
    # "Vasai_Fort_Museum_Vasai": [
    #     "Category:Interior of the Vasai Fort Museum"
    # ],
    # "Veraval_Museum_Veraval": [
    #     "Category:Interior of the Veraval Museum"
    # ],
    # "Vizianagaram_Museum_Vizianagaram": [
    #     "Category:Interior of the Vizianagaram Museum"
    # ],
    # "West_Bengal_Police_Museum_Kolkata": [
    #     "Category:Interior of the West Bengal Police Museum"
    # ],
    #   "Zoological_Museum_Kolkata": [
    #     "Category:Interior of the Zoological Museum, Kolkata"
    # ],
    # "Almora_Museum_Almora": [
    #     "Category:Interior of the Almora Museum"
    # ],
    # "Archaeological_Museum_Mathura": [
    #     "Category:Interior of the Archaeological Museum, Mathura"
    # ],
    # "Aurangabad_Caves_Museum_Aurangabad": [
    #     "Category:Interior of the Aurangabad Caves Museum"
    # ],
    # "Bastar_Tribal_Museum_Bastar": [
    #     "Category:Interior of the Bastar Tribal Museum"
    # ],
    # "Chamba_Museum_Chamba": [
    #     "Category:Interior of the Chamba Museum"
    # ],
    # "Coorg_Museum_Coorg": [
    #     "Category:Interior of the Coorg Museum"
    # ],
    # "Darbhanga_Museum_Darbhanga": [
    #     "Category:Interior of the Darbhanga Museum"
    # ],
    # "Dharamshala_Museum_Dharamshala": [
    #     "Category:Interior of the Dharamshala Museum"
    # ],
    #   "Dehradun_Fossil_Museum_Dehradun": [
    #     "Category:Interior of the Dehradun Fossil Museum"
    # ],
    # "Gandhinagar_Science_Museum_Gandhinagar": [
    #     "Category:Interior of the Gandhinagar Science Museum"
    # ],
    # "Vellore_Fort_Museum_Vellore": [
    #     "Category:Interior of the Vellore Fort Museum"
    # ],
    # "Wayanad_Heritage_Museum_Wayanad": [
    #     "Category:Interior of the Wayanad Heritage Museum"
    # ],
    # "West_Bengal_Police_Museum_Kolkata": [
    #     "Category:Interior of the West Bengal Police Museum"
    # ],
    # "Zawar_Mines_Museum_Udaipur": [
    #     "Category:Interior of the Zawar Mines Museum"
    # ],
    # "Adilabad_Museum_Adilabad": [
    #     "Category:Interior of the Adilabad Museum"
    # ]
#        "Almora_Museum_Almora": [
#         "Category:Interior of the Almora Museum"
#     ],
#     "Asansol_Museum_Asansol": [
#         "Category:Interior of the Asansol Museum"
#     ],
#     "Balasore_Museum_Balasore": [
#         "Category:Interior of the Balasore Museum"
#     ],
#     "Bankura_Museum_Bankura": [
#         "Category:Interior of the Bankura Museum"
#     ],
#     "Bastar_Tribal_Museum_Bastar": [
#         "Category:Interior of the Bastar Tribal Museum"
#     ],
#     "Chakradharpur_Museum_Chakradharpur": [
#         "Category:Interior of the Chakradharpur Museum"
#     ],
#     "Coorg_Museum_Coorg": [
#         "Category:Interior of the Coorg Museum"
#     ],
#     "Darrang_Museum_Mangaldoi": [
#         "Category:Interior of the Darrang Museum"
#     ],
#      "Dharamshala_Museum_Dharamshala": [
#         "Category:Interior of the Dharamshala Museum"
#     ],
#     "Darbhanga_Museum_Darbhanga": [
#         "Category:Interior of the Darbhanga Museum"
#     ],
#     "Chamba_Museum_Chamba": [
#         "Category:Interior of the Chamba Museum"
#     ],
#     "Assam_State_Museum_Guwahati": [
#         "Category:Interiors of Assam State Museum"
#     ],
#     "Bhilai_Steel_Plant_Museum_Bhilai": [
#         "Category:Interior of Bhilai Steel Plant Museum"
#     ],
#       "Balangir_Museum_Balangir": [
#         "Category:Interior of the Balangir Museum"
#     ],
#     "Bhadrak_Museum_Bhadrak": [
#         "Category:Interior of the Bhadrak Museum"
#     ],
#     "Bhandara_Museum_Bhandara": [
#         "Category:Interior of the Bhandara Museum"
#     ],
#     "Chhattisgarh_State_Museum_Raipur": [
#         "Category:Interior of the Chhattisgarh State Museum"
#     ],
#     "Dehradun_Fossil_Museum_Dehradun": [
#         "Category:Interior of the Dehradun Fossil Museum"
#     ],
#      "Chakradharpur_Museum_Chakradharpur": [
#         "Category:Interior of the Chakradharpur Museum"
#     ],
#     "Chamba_Museum_Chamba": [
#         "Category:Interior of the Chamba Museum"
#     ],
#     "Coorg_Museum_Coorg": [
#         "Category:Interior of the Coorg Museum"
#     ],
#     "Darbhanga_Museum_Darbhanga": [
#         "Category:Interior of the Darbhanga Museum"
#     ],
#     "Darrang_Museum_Mangaldoi": [
#         "Category:Interior of the Darrang Museum"
#     ]
#     "Dibrugarh_Museum_Dibrugarh": [
#     "Category:Dibrugarh Museum, Dibrugarh",
#     "Category:Highlights Assam's local history and ethnography."
# ],

# "Dindigul_Museum_Dindigul": [
#     "Category:Dindigul Museum, Dindigul",
#     "Category:Preserves regional artifacts and Dindigul's historical records."
# ],

# "East_Singhbhum_Museum_Jamshedpur": [
#     "Category:East Singhbhum Museum, Jamshedpur",
#     "Category:Focuses on the area's industrial heritage and mining history."
# ],

# "Erode_Museum_Erode": [
#     "Category:Erode Museum, Erode",
#     "Category:Exhibits local history and textile-related cultural items."
# ],

# "Fatehgarh_Sahib_Museum_Fatehgarh_Sahib": [
#     "Category:Fatehgarh Sahib Museum, Fatehgarh Sahib",
#     "Category:Documents the region's Sikh and local historical events."
# ],

# "Firozabad_Museum_Firozabad": [
#     "Category:Firozabad Museum, Firozabad",
#     "Category:Showcases local history and the city's glass-making heritage."
# ],

# "Gadchiroli_Museum_Gadchiroli": [
#     "Category:Gadchiroli Museum, Gadchiroli",
#     "Category:Features tribal art and cultural artifacts of the region."
# ],

# "Gandhinagar_Museum_Gandhinagar": [
#     "Category:Gandhinagar Museum, Gandhinagar",
#     "Category:Displays state-level historical collections and exhibits."
# ],

# "Ganjam_Museum_Berhampur": [
#     "Category:Ganjam Museum, Berhampur",
#     "Category:Highlights Ganjam's local history and cultural heritage."
# ],

# "Garhwal_Museum_Pauri_Garhwal": [
#     "Category:Garhwal Museum, Pauri Garhwal",
#     "Category:Focuses on Garhwal culture, traditions, and artifacts."
# ],

# "Giridih_Museum_Giridih": [
#     "Category:Giridih Museum, Giridih",
#     "Category:Preserves the district's history and archaeological finds."
# ],

# "Gonda_Museum_Gonda": [
#     "Category:Gonda Museum, Gonda",
#     "Category:Exhibits regional history and cultural materials."
# ],

# "Gopalganj_Museum_Gopalganj": [
#     "Category:Gopalganj Museum, Gopalganj",
#     "Category:Maintains local historical records and artifacts."
# ],

# "Gorakhpur_Museum_Gorakhpur": [
#     "Category:Gorakhpur Museum, Gorakhpur",
#     "Category:Showcases Gorakhpur's historical and cultural collections."
# ],

# "Gulbarga_Museum_Gulbarga": [
#     "Category:Gulbarga Museum, Gulbarga",
#     "Category:Displays regional history and medieval relics."
# ],

# "Guntur_Museum_Guntur": [
#     "Category:Guntur Museum, Guntur",
#     "Category:Focuses on Guntur's historical, cultural and archaeological items."
# ],

# "Hamirpur_Museum_Hamirpur": [
#     "Category:Hamirpur Museum, Hamirpur",
#     "Category:Features Himachali culture and regional heritage exhibits."
# ],

# "Harda_Museum_Harda": [
#     "Category:Harda Museum, Harda",
#     "Category:Preserves local history and historical documents of the region."
# ],

# "Hardoi_Museum_Hardoi": [
#     "Category:Hardoi Museum, Hardoi",
#     "Category:Shows artifacts and records relating to local history."
# ],

# "Hassan_Museum_Hassan": [
#     "Category:Hassan Museum, Hassan",
#     "Category:Contains artifacts reflecting Hassan district's past."
# ],

# "Hazaribagh_Museum_Hazaribagh": [
#     "Category:Hazaribagh Museum, Hazaribagh",
#     "Category:Exhibits local history, tribal culture, and regional archaeology."
# ],

# "Hoshiarpur_Museum_Hoshiarpur": [
#     "Category:Hoshiarpur Museum, Hoshiarpur",
#     "Category:Presents Hoshiarpur's historical collections and objects."
# ],

# "Hubli_Museum_Hubli": [
#     "Category:Hubli Museum, Hubli",
#     "Category:Documents Hubli's regional history and cultural heritage."
# ],

# "Hyderabad_Archaeological_Museum_Hyderabad": [
#     "Category:Hyderabad Archaeological Museum, Hyderabad",
#     "Category:Houses archaeological finds and ancient regional artifacts."
# ],

# "Imphal_Museum_Imphal": [
#     "Category:Imphal Museum, Imphal",
#     "Category:Highlights Manipur's cultural heritage and traditional arts."
# ],

# "Indore_Museum_Indore": [
#     "Category:Indore Museum, Indore",
#     "Category:Displays central India's history and archaeological items."
# ],

# "Jabalpur_Museum_Jabalpur": [
#     "Category:Jabalpur Museum, Jabalpur",
#     "Category:Showcases local history, fossils and regional artifacts."
# ],

# "Jagdalpur_Museum_Jagdalpur": [
#     "Category:Jagdalpur Museum, Jagdalpur",
#     "Category:Focuses on tribal culture and Chhattisgarh's heritage."
# ],

# "Jaipur_Museum_Jaipur": [
#     "Category:Jaipur Museum, Jaipur",
#     "Category:Has collections illustrating Rajasthan's royal and cultural past."
# ],

# "Jalandhar_Museum_Jalandhar": [
#     "Category:Jalandhar Museum, Jalandhar",
#     "Category:Exhibits local history and traditional artifacts of the area."
# ],

# "Jamnagar_Museum_Jamnagar": [
#     "Category:Jamnagar Museum, Jamnagar",
#     "Category:Preserves the maritime and regional history of Jamnagar."
# ],

# "Jashpur_Museum_Jashpur": [
#     "Category:Jashpur Museum, Jashpur",
#     "Category:Displays local history and tribal cultural objects from the district."
# ],

# "Jatani_Museum_Jatani": [
#     "Category:Jatani Museum, Jatani",
#     "Category:Highlights the historical heritage of the Jatani region."
# ],

# "Jehanabad_Museum_Jehanabad": [
#     "Category:Jehanabad Museum, Jehanabad",
#     "Category:Contains artefacts and records of Jehanabad's local history."
# ],

# "Jhabua_Museum_Jhabua": [
#     "Category:Jhabua Museum, Jhabua",
#     "Category:Focuses on tribal arts and cultural traditions of Jhabua."
# ],

# "Jhansi_Museum_Jhansi": [
#     "Category:Jhansi Museum, Jhansi",
#     "Category:Documents Jhansi's historical role and regional heritage."
# ],

# "Jhargram_Museum_Jhargram": [
#     "Category:Jhargram Museum, Jhargram",
#     "Category:Highlights tribal culture and local historical artifacts."
# ],

# "Jodhpur_Museum_Jodhpur": [
#     "Category:Jodhpur Museum, Jodhpur",
#     "Category:Showcases Jodhpur's royal history and cultural collections."
# ],

# "Kaimur_Museum_Kaimur": [
#     "Category:Kaimur Museum, Kaimur",
#     "Category:Presents the district's historical artifacts and folk culture."
# ],

# "Kalimpong_Museum_Kalimpong": [
#     "Category:Kalimpong Museum, Kalimpong",
#     "Category:Features Himalayan culture and regional historical items."
# ],

# "Kalyan_Museum_Kalyan": [
#     "Category:Kalyan Museum, Kalyan",
#     "Category:Preserves local history and artifacts of the Kalyan area."
# ],

# "Kamrup_Museum_Guwahati": [
#     "Category:Kamrup Museum, Guwahati",
#     "Category:Displays Assam's cultural history and archaeological finds."
# ],

# "Kancheepuram_Museum_Kancheepuram": [
#     "Category:Kancheepuram Museum, Kancheepuram",
#     "Category:Documents the temple town's history and religious artifacts."
# ],

# "Kannur_Museum_Kannur": [
#     "Category:Kannur Museum, Kannur",
#     "Category:Showcases Malabar history and local cultural objects."
# ],

# "Kapurthala_Museum_Kapurthala": [
#     "Category:Kapurthala Museum, Kapurthala",
#     "Category:Preserves Kapurthala's royal heritage and historical exhibits."
# ],

# "Karimnagar_Museum_Karimnagar": [
#     "Category:Karimnagar Museum, Karimnagar",
#     "Category:Highlights regional history and archaeological collections."
# ],

# "Karur_Museum_Karur": [
#     "Category:Karur Museum, Karur",
#     "Category:Displays Karur's ancient trade and cultural artifacts."
# ],

# "Kasaragod_Museum_Kasaragod": [
#     "Category:Kasaragod Museum, Kasaragod",
#     "Category:Focuses on local culture and coastal traditions of Kasaragod."
# ],

# "Katihar_Museum_Katihar": [
#     "Category:Katihar Museum, Katihar",
#     "Category:Documents the district's historical and cultural legacy."
# ],

# "Kendrapara_Museum_Kendrapara": [
#     "Category:Kendrapara Museum, Kendrapara",
#     "Category:Exhibits local history and coastal cultural heritage."
# ],

# "Khandwa_Museum_Khandwa": [
#     "Category:Khandwa Museum, Khandwa",
#     "Category:Displays artifacts reflecting the Nimar region's past."
# ],

# "Kheri_Museum_Kheri": [
#     "Category:Kheri Museum, Kheri",
#     "Category:Focuses on district history and traditional items."
# ],

# "Khordha_Museum_Khordha": [
#     "Category:Khordha Museum, Khordha",
#     "Category:Presents Khordha's historical artifacts and records."
# ],

# "Kishanganj_Museum_Kishanganj": [
#     "Category:Kishanganj Museum, Kishanganj",
#     "Category:Showcases the district's historical and cultural objects."
# ],

# "Kochi_Museum_Kochi": [
#     "Category:Kochi Museum, Kochi",
#     "Category:Highlights Kochi's maritime history and colonial-era artifacts."
# ],

# "Kohima_Museum_Kohima": [
#     "Category:Kohima Museum, Kohima",
#     "Category:Celebrates Nagaland's tribal heritage and traditional crafts."
# ],

# "Kolhapur_Museum_Kolhapur": [
#     "Category:Kolhapur Museum, Kolhapur",
#     "Category:Features Maratha history and regional cultural collections."
# ],

# "Kollam_Museum_Kollam": [
#     "Category:Kollam Museum, Kollam",
#     "Category:Preserves the coastal and cultural history of Kollam."
# ],

# "Koraput_Museum_Koraput": [
#     "Category:Koraput Museum, Koraput",
#     "Category:Highlights tribal arts and Koraput's cultural traditions."
# ],

# "Kota_Museum_Kota": [
#     "Category:Kota Museum, Kota",
#     "Category:Exhibits local history and Rajasthan's regional heritage."
# ],

# "Kottayam_Museum_Kottayam": [
#     "Category:Kottayam Museum, Kottayam",
#     "Category:Documents Kottayam's cultural and historical artifacts."
# ],

# "Kozhikode_Museum_Kozhikode": [
#     "Category:Kozhikode Museum, Kozhikode",
#     "Category:Showcases Malabar trade history and regional culture."
# ],

# "Krishna_District_Museum_Vijayawada": [
#     "Category:Krishna District Museum, Vijayawada",
#     "Category:Highlights the district's archaeological and historical finds."
# ],

# "Kullu_Museum_Kullu": [
#     "Category:Kullu Museum, Kullu",
#     "Category:Focuses on Himachali culture and mountain traditions."
# ],

# "Kurnool_Museum_Kurnool": [
#     "Category:Kurnool Museum, Kurnool",
#     "Category:Displays historical artifacts from the Kurnool region."
# ],

# "Lakhimpur_Museum_Lakhimpur": [
#     "Category:Lakhimpur Museum, Lakhimpur",
#     "Category:Preserves local history and Assamese cultural exhibits."
# ],

# "Lalitpur_Museum_Lalitpur": [
#     "Category:Lalitpur Museum, Lalitpur",
#     "Category:Showcases Bundelkhand's historical heritage and artifacts."
# ],

# "Latur_Museum_Latur": [
#     "Category:Latur Museum, Latur",
#     "Category:Documents Marathwada history and local cultural items."
# ],

# "Lohardaga_Museum_Lohardaga": [
#     "Category:Lohardaga Museum, Lohardaga",
#     "Category:Highlights regional history and tribal artifacts of Lohardaga."
# ],

# "Ludhiana_Museum_Ludhiana": [
#     "Category:Ludhiana Museum, Ludhiana",
#     "Category:Preserves Punjab's cultural and industrial heritage."
# ],

# "Madurai_Museum_Madurai": [
#     "Category:Madurai Museum, Madurai",
#     "Category:Displays ancient Tamil art and temple-related artifacts."
# ],

# "Mahbubnagar_Museum_Mahbubnagar": [
#     "Category:Mahbubnagar Museum, Mahbubnagar",
#     "Category:Features Telangana's local history and cultural items."
# ],

# "Mandsaur_Museum_Mandsaur": [
#     "Category:Mandsaur Museum, Mandsaur",
#     "Category:Exhibits archaeological finds and historical artifacts."
# ],

# "Mangaluru_Museum_Mangaluru": [
#     "Category:Mangaluru Museum, Mangaluru",
#     "Category:Highlights coastal Karnataka history and maritime heritage."
# ],

# "Manipal_Museum_Manipal": [
#     "Category:Manipal Museum, Manipal",
#     "Category:Displays regional history and academic collections."
# ],

# "Mathura_Museum_Mathura": [
#     "Category:Mathura Museum, Mathura",
#     "Category:Focuses on Mathura's religious and ancient historical artifacts."
# ],

# "Meerut_Museum_Meerut": [
#     "Category:Meerut Museum, Meerut",
#     "Category:Showcases Meerut's colonial and military history."
# ],

# "Midnapore_Museum_Midnapore": [
#     "Category:Midnapore Museum, Midnapore",
#     "Category:Documents Midnapore's historical events and cultural heritage."
# ],

# "Mirzapur_Museum_Mirzapur": [
#     "Category:Mirzapur Museum, Mirzapur",
#     "Category:Highlights local history and pottery/trade traditions."
# ],

# "Moradabad_Museum_Moradabad": [
#     "Category:Moradabad Museum, Moradabad",
#     "Category:Exhibits the city's metalwork history and local artifacts."
# ]
  "New_Delhi_Railway_Museum_New_Delhi": [
        "Category:National Rail Museum (India)",
        "Category:Interiors of National Rail Museum (India)"
    ],
    "Nilgiri_Museum_Ooty": [
        "Category:Government Museum, Ooty"
    ],
    "Panaji_Museum_Panaji": [
        "Category:Goa State Museum"
    ],
    "Pune_Museum_Pune": [
        "Category:Raja Dinkar Kelkar Museum"
    ],
    "Rajkot_Museum_Rajkot": [
        "Category:Watson Museum"
    ],
    "Shimla_State_Museum_Shimla": [
        "Category:State Museum, Shimla",
        "Category:Interiors of State Museum, Shimla"
    ],
    "Srinagar_Museum_Srinagar": [
        "Category:Srinagar museums"
    ],
    "Thanjavur_Archaeological_Museum_Thanjavur": [
        "Category:Thanjavur Art Gallery"
    ],
    "Thiruvananthapuram_Museum_Thiruvananthapuram": [
        "Category:Napier Museum",
        "Category:Interiors of Napier Museum"
    ],
    "Thrissur_Museum_Thrissur": [
        "Category:Thrissur Archaeological Museum"
    ],
    "Tirunelveli_Museum_Tirunelveli": [
        "Category:Government Museum, Tirunelveli"
    ],
    "Vadodara_Museum_Vadodara": [
        "Category:Vadodara Museum & Picture Gallery",
        "Category:Interiors of Vadodara Museum & Picture Gallery"
    ],
    "Varanasi_Museum_Varanasi": [
        "Category:Bharat Kala Bhavan"
    ],
    "Vellore_Museum_Vellore": [
        "Category:Government Museum, Vellore"
    ],
    "Vidisha_Museum_Vidisha": [
        "Category:Vidisha District Museum"
    ],
    "Warangal_Museum_Warangal": [
        "Category:Warangal museums"
    ],
    "Wayanad_Heritage_Museum_Wayanad": [
        "Category:Wayanad Heritage Museum"
    ],
    "Zoological_Museum_Kolkata": [
        "Category:Zoological Museum, Kolkata"
    ],
     "Panchkula_Museum_Panchkula": [
        "Category:National Cactus and Succulent Botanical Garden and Research Centre"
    ],

    "Patan_Museum_Patan": [
        "Category:Patan Museum"
    ],

    "Raipur_Museum_Raipur": [
        "Category:Raipur museums"
    ],

    "Rajahmundry_Museum_Rajahmundry": [
        "Category:Rajahmundry"
    ],

    "Rajnandgaon_Museum_Rajnandgaon": [
        "Category:Rajnandgaon"
    ],

    "Raurkela_Museum_Raurkela": [
        "Category:Rourkela"
    ],

    "Rewa_Museum_Rewa": [
        "Category:Rewa"
    ],

    "Rohtak_Museum_Rohtak": [
        "Category:Rohtak"
    ],

    "Sagar_Museum_Sagar": [
        "Category:Sagar"
    ],

    "Saharanpur_Museum_Saharanpur": [
        "Category:Saharanpur"
    ],

    "Salem_Museum_Salem": [
        "Category:Salem, Tamil Nadu"
    ],

    "Sambalpur_Museum_Sambalpur": [
        "Category:Sambalpur"
    ],

    "Sangli_Museum_Sangli": [
        "Category:Sangli"
    ],

    "Satara_Museum_Satara": [
        "Category:Satara"
    ],

    "Seoni_Museum_Seoni": [
        "Category:Seoni district"
    ],

    "Sikar_Museum_Sikar": [
        "Category:Sikar"
    ],

    "Silchar_Museum_Silchar": [
        "Category:Silchar"
    ],

    "Siliguri_Museum_Siliguri": [
        "Category:Siliguri"
    ],

    "Singrauli_Museum_Singrauli": [
        "Category:Singrauli"
    ],

    "Solapur_Museum_Solapur": [
        "Category:Solapur"
    ],

    "Sonipat_Museum_Sonipat": [
        "Category:Sonipat"
    ],

    "Tezpur_Museum_Tezpur": [
        "Category:Tezpur"
    ],

    "Tumkur_Museum_Tumkur": [
        "Category:Tumkur"
    ],

    "Udupi_Museum_Udupi": [
        "Category:Udupi"
    ],

    "Una_Museum_Una": [
        "Category:Una district"
    ],

    "Varanasi_Museum_Varanasi": [
        "Category:Bharat Kala Bhavan"
    ],

    "Yadgir_Museum_Yadgir": [
        "Category:Yadgir"
    ],

    "Aizawl_Museum_Aizawl": [
        "Category:Mizoram State Museum"
    ],

    "Alappuzha_Maritime_Museum_Alappuzha": [
        "Category:Alleppey"
    ],

    "Ambedkar_Memorial_Indore": [
        "Category:Dr. Bhimrao Ambedkar memorial sites"
    ],

    "Anantapur_District_Museum_Anantapur": [
        "Category:Anantapur"
    ],
      "Archaeological_Museum_Raipur": [
        "Category:Raipur"
    ],

    "Assam_State_Museum_Guwahati": [
        "Category:Assam State Museum"
    ],

    "Balangir_Museum_Balangir": [
        "Category:Balangir"
    ],

    "Barmer_Museum_Barmer": [
        "Category:Barmer"
    ],

    "Begusarai_Museum_Begusarai": [
        "Category:Begusarai"
    ],

    "Bengal_Museum_of_Industrial_Archaeology_Kolkata": [
        "Category:Industrial archaeology in India",
        "Category:Kolkata"
    ],

    "Bhadrak_Museum_Bhadrak": [
        "Category:Bhadrak"
    ],

    "Bhandara_Museum_Bhandara": [
        "Category:Bhandara"
    ],

    "Bhilai_Steel_Plant_Museum_Bhilai": [
        "Category:Bhilai Steel Plant",
        "Category:Bhilai"
    ],

    "Bilaspur_Tribal_Museum_Bilaspur": [
        "Category:Bilaspur"
    ],

    "Brahmapur_Museum_Brahmapur": [
        "Category:Brahmapur"
    ],

    "Chennai_Museum_Chennai": [
        "Category:Government Museum, Chennai"
    ],

    "Chhattisgarh_State_Museum_Raipur": [
        "Category:Chhattisgarh State Museum"
    ],

    "Coimbatore_Museum_Coimbatore": [
        "Category:Coimbatore"
    ],

    "Dehradun_Fossil_Museum_Dehradun": [
        "Category:Dehradun"
    ],

    "Dhanbad_Museum_Dhanbad": [
        "Category:Dhanbad"
    ],

    "Gandhinagar_Science_Museum_Gandhinagar": [
        "Category:Gandhinagar"
    ],

    "Vasai_Fort_Museum_Vasai": [
        "Category:Vasai Fort"
    ],

    "Vellore_Fort_Museum_Vellore": [
        "Category:Vellore Fort"
    ],

    "Veraval_Museum_Veraval": [
        "Category:Veraval"
    ],

    "Vizianagaram_Museum_Vizianagaram": [
        "Category:Vizianagaram"
    ],

    "Wayanad_Heritage_Museum_Wayanad": [
        "Category:Wayanad Heritage Museum"
    ],

    "West_Bengal_Police_Museum_Kolkata": [
        "Category:West Bengal Police Museum"
    ],

    "Yamunanagar_Museum_Yamunanagar": [
        "Category:Yamunanagar"
    ],

    "Zawar_Mines_Museum_Udaipur": [
        "Category:Zawar"
    ],

    "Zoological_Museum_Kolkata": [
        "Category:Zoological Museum, Kolkata"
    ]
}



def make_folder(path):
    os.makedirs(path, exist_ok=True)

def get_filename_from_url(url):
    path = urlparse(url).path
    return unquote(os.path.basename(path))

def api_call(params):
    try:
        r = requests.get(WIKIMEDIA_API, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r
    except:
        return None

def get_category_files(category_title, limit=50, next_token=None):
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category_title,
        "cmnamespace": 6,
        "cmlimit": limit
    }
    if next_token:
        params["cmcontinue"] = next_token

    r = api_call(params)
    if not r:
        return [], None

    data = r.json()
    members = data.get("query", {}).get("categorymembers", [])
    next_token = data.get("continue", {}).get("cmcontinue")
    return members, next_token

def get_image_info(titles):
    if not titles:
        return []

    params = {
        "action": "query",
        "format": "json",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url|size|mime"
    }

    r = api_call(params)
    if not r:
        return []

    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    output = []

    for page_id, page in pages.items():
        info = page.get("imageinfo")
        if info:
            img = info[0]
            output.append({
                "title": page.get("title"),
                "url": img.get("url"),
                "width": img.get("width", 0),
                "height": img.get("height", 0)
            })

    return output

def download_image(url, save_path):
    try:
        with requests.get(url, stream=True, headers=HEADERS, timeout=60) as r:
            r.raise_for_status()
            temp = save_path + ".part"
            with open(temp, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            os.replace(temp, save_path)
        return True
    except:
        if os.path.exists(save_path + ".part"):
            os.remove(save_path + ".part")
        return False

def create_thumbnail(image_path, thumb_path):
    try:
        img = Image.open(image_path)
        img.thumbnail(THUMBNAIL_SIZE)
        img.save(thumb_path, "JPEG", quality=80)
    except:
        pass

def download_for_museum(museum_name, categories):
    print("\nDownloading for:", museum_name)

    museum_folder = os.path.join(OUTPUT_ROOT, museum_name)
    thumb_folder = os.path.join(museum_folder, "thumbnails")

    make_folder(museum_folder)
    if CREATE_THUMBNAILS:
        make_folder(thumb_folder)

    downloaded = 0
    used_urls = set()

    for category in categories:
        if downloaded >= MAX_IMAGES_PER_MUSEUM:
            break

        print("  Category:", category)
        next_token = None

        while downloaded < MAX_IMAGES_PER_MUSEUM:
            members, next_token = get_category_files(category, next_token=next_token)
            if not members:
                break

            titles = [m["title"] for m in members]
            images = get_image_info(titles)

            for img in images:
                if downloaded >= MAX_IMAGES_PER_MUSEUM:
                    break

                url = img["url"]
                w = img["width"]
                h = img["height"]

                if not url or url in used_urls:
                    continue

                if w < MIN_WIDTH or h < MIN_HEIGHT:
                    continue

                file_name = get_filename_from_url(url)
                save_path = os.path.join(museum_folder, file_name)

                if os.path.exists(save_path):
                    base, ext = os.path.splitext(file_name)
                    n = 1
                    while os.path.exists(os.path.join(museum_folder, f"{base}_{n}{ext}")):
                        n += 1
                    save_path = os.path.join(museum_folder, f"{base}_{n}{ext}")

                print("    Downloading:", file_name)

                ok = download_image(url, save_path)
                if ok:
                    used_urls.add(url)
                    downloaded += 1

                    if CREATE_THUMBNAILS:
                        thumb_name = os.path.splitext(os.path.basename(save_path))[0] + ".jpg"
                        thumb_path = os.path.join(thumb_folder, thumb_name)
                        create_thumbnail(save_path, thumb_path)

                time.sleep(SLEEP)

            if not next_token:
                break

            time.sleep(SLEEP)

    print("  Total downloaded:", downloaded)



def main():
    make_folder(OUTPUT_ROOT)

    for museum, categories in MANUAL_CATEGORIES.items():
        download_for_museum(museum, categories)

    print("\nDownload completed. Check museum_images folder.")

if __name__ == "__main__":
    main()
