#!/usr/bin/env python3
"""Builds a single self-contained index.html for the SCyPS center site (image-rich version).

All publication and grant data live here so the HTML is generated without
hand-typed DOIs. Publications: Crossref (2025-2026) + UML faculty pages.
Grants: figures confirmed on the director's NSF Current & Pending (Sept 2026).
"""
import html, json, re

import sys, datetime, os, hashlib
OUT = next((a for a in sys.argv[1:] if not a.startswith("-")), "index.html")   # run: python3 build_site.py [output path]

# ---------------------------------------------------------------- people
CORE = {"Vokkarane", "Aghara", "Arias", "Evans", "Lin", "Luo", "Robinette", "Son", "Tseng", "Xie"}   # director + center faculty
CORE_INITIAL = {"Son": "S", "Lin": "Y", "Luo": "Y", "Cao": "Y", "Yu": "H", "Xie": "Y"}   # common surnames: bold only with this first initial

FACULTY = {
    "director": {
        "name": "Vinod M. Vokkarane", "photo": "vokkarane", "title": "Professor, Electrical and Computer Engineering", "title2": "Director, Center for Smart Cyber-Physical Systems (SCyPS)",
        "areas": "Cyber-physical systems, smart grid cybersecurity and resilience, optical and 6G network optimization, AI/ML for networked systems",
        "email": "vinod_vokkarane@uml.edu", "phone": "978-934-3345", "office": "Ball Hall 409",
        "url": "https://www.uml.edu/engineering/electrical-computer/faculty/vokkarane-vinod.aspx",
        "bio": ("The center was founded on October 1, 2019 by Vinod Vokkarane, Martin Margala, Yan Luo, Sukesh Aghara, and Yuanchang Xie. Vokkarane served on the founding Board of Directors from October 2019 to July 2021 and has been director since August 2021. His group works on secure and resilient "
                "cyber-physical power systems, quality-of-transmission-aware multi-band and space-division "
                "multiplexed optical networks, and open-source tools for reproducible network research. He is a "
                "Senior Member of the IEEE, serves on the editorial board of the IEEE/Optica Journal of Optical "
                "Communications and Networking, co-authored the Springer book Optical Burst Switched Networks, and "
                "has shared best paper awards at IEEE GLOBECOM, IEEE ANTS, and ONDM. He is the PI of the NSF MRI "
                "SUMMIT testbed award and a technical advisor to the UMass Lowell Applied Research Corporation (UMLARC)."),
    },
    "core": [
        {"name": "Sukesh Aghara", "photo": "aghara", "title": "Professor, Chemical and Nuclear Engineering; Senior Advisor to the Chancellor on Nuclear Energy Strategies",
         "areas": "Nuclear security and safeguards, cybersecurity of nuclear facilities, advanced reactor modeling, nuclear energy for decarbonization", "email": "Sukesh_Aghara@uml.edu", "phone": "978-934-3115", "role": "Co-founder of the center in 2019 and founding co-director for energy. Leads the nuclear energy and security thrust and the Massachusetts Advanced Nuclear and Fusion Energy Roadmaps; directs the Integrated Nuclear Security and Safeguards Laboratory (INSSL) and co-directs the IAEA-funded Intercontinental Nuclear Institute. Editor of The Oxford Handbook of Nuclear Security (Oxford University Press). Associate Dean for Research of the Francis College of Engineering from 2021 to 2026 and Director of the Nuclear Engineering Program from 2017 to 2025. Chair of the Nuclear Engineering Department Heads Organization for 2024 to 2025, and elected in 2024 to the board of the ASEE Engineering Research Council.", "url": "https://www.uml.edu/engineering/chemical/faculty/aghara-sukesh.aspx"},
        {"name": "Orlando Arias", "photo": "arias", "title": "Assistant Professor, Electrical and Computer Engineering",
         "areas": "Hardware security, hardware-software co-design, embedded and microarchitectural security, cyber security",
         "email": "Orlando_Arias@uml.edu", "phone": "978-934-3476", "office": "Ball Hall 407A",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/arias-orlando.aspx",
         "role": "Co-PI on the SUMMIT testbed and the ONR post-disaster restoration project; leads hardware attestation and embedded security for grid devices."},
        {"name": "Nicholas G. Evans", "photo": "evans", "title": "Associate Professor, Philosophy, College of Fine Arts, Humanities and Social Sciences",
         "areas": "Ethics of emerging technologies and national security, dual-use research, bioethics and public health ethics, military ethics", "email": "Nicholas_Evans@uml.edu", "phone": "978-934-3996",
         "url": "https://www.uml.edu/fahss/political-science/faculty/evans-nicholas.aspx",
         "role": "Ethics lead for the center's people-in-the-loop theme: trust, ethics, and human performance in systems whose failure has physical consequences. PI of the NSF award on ethical algorithms for autonomous vehicles, with Xie as Co-PI, and co-author on its papers; lead investigator on two pending proposals with the director, to Schmidt Sciences and to NSF, that apply AI methods to the history and ethics of health information."},
        {"name": "Yuzhang Lin", "photo": "lin", "inst": "New York University", "title": "Associate Professor, Electrical and Computer Engineering, NYU Tandon School of Engineering",
         "areas": "Smart grid and renewable energy: modeling, situational awareness, cyber-physical resilience, machine learning applications",
         "email": "yuzhang.lin@nyu.edu", "phone": "", "office": "",
         "url": "https://engineering.nyu.edu/faculty/yuzhang-lin",
         "role": "External center member; UMass Lowell ECE faculty 2018 to 2023. NSF CAREER awardee; Co-PI on SUMMIT and the ONR post-disaster restoration project, and a co-author on the center's smart grid papers."},
        {"name": "Yan Luo", "photo": "luo", "title": "Professor, Electrical and Computer Engineering; Robotics",
         "areas": "Cyber-physical systems, machine learning, computer networks, computer architecture",
         "role": "Co-founder of the center in 2019 and founding co-director for healthcare. Leads the AI for cyber-physical control thrust; senior personnel on SUMMIT; PI of the NSF-funded campus science network the center builds on and of the NSF PFI-RP BioSPACE project on pathogen biosensing in aquaculture. Best Paper Award at IFIP/IEEE IM 2021 and Best Experiences Paper Award at IM 2019.",
         "email": "yan_luo@uml.edu", "phone": "978-934-2592", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/luo-yan.aspx"},
        {"name": "Paul Robinette", "photo": "robinette", "title": "Associate Professor, Electrical and Computer Engineering; Associate Chair for M.S. Programs",
         "areas": "Robotics, human-robot interaction, trust in autonomous systems, multi-robot coordination, field and marine autonomy",
         "email": "Paul_Robinette@uml.edu", "phone": "978-934-3347",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/robinette-paul.aspx",
         "role": "Brings robotics and human-robot interaction to the center: trust and transparency between people and the machines they work with, multi-agent coordination, and autonomy for environments people should not enter. Works on the connected transportation, health, and infrastructure thrust, and connects the center to the Printed Electronics Research Collaborative and the Raytheon UMass Lowell Research Institute."},
        {"name": "Seung Woo Son", "photo": "son", "title": "Associate Professor, Electrical and Computer Engineering",
         "areas": "High performance computing, parallel I/O and data-intensive computing, compiler optimizations, embedded systems",
         "email": "SeungWoo_Son@uml.edu", "phone": "978-934-6846", "office": "Ball Hall 419",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/son-seung-woo.aspx",
         "role": "Leads the high performance computing and data integrity thrust. NSF CAREER awardee (2018); brings HPC, silent-data-corruption detection, and on-device stream analytics to the center's data-intensive CPS work."},
        {"name": "Lewis Tseng", "photo": "tseng", "title": "Associate Professor, Electrical and Computer Engineering",
         "areas": "Fault-tolerant distributed systems and consensus, state machine replication, blockchain systems, and edge computing for cyber-physical systems",
         "email": "Lewis_Tseng@uml.edu", "phone": "", "office": "Ball Hall, 3rd floor",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/tseng-lewis.aspx",
         "role": "NSF CAREER awardee on fault-tolerant edge computing for cyber-physical systems under cyber attack (award #2449640 at UMass Lowell, $342K from Sept 2024); PI of an NSF planning award for federated AI-ready cyberinfrastructure for advanced microscopy (2026); Co-PI on SUMMIT. 2026 ECE Department Teaching Excellence Award. Joined UMass Lowell in 2024 after Clark University, Boston College, and Toyota InfoTechnology Center."},
        {"name": "Yuanchang Xie", "photo": "xie", "title": "Professor, Civil and Environmental Engineering",
         "areas": "Transportation safety, intelligent transportation systems, connected and automated vehicles, transportation data analytics and AI",
         "role": "Co-founder of the center in 2019 and founding co-director for transportation. Leads the connected transportation thrust; PI or Co-PI of the USDOT, MassDOT, and NETC transportation portfolio. Associate Editor of Accident Analysis & Prevention and of the IEEE Intelligent Transportation Systems Conference; Kikuchi-Karlaftis Best Paper Award (TRB, 2020) and the George N. Saridis Best Transactions Paper Award of IEEE Transactions on Intelligent Transportation Systems (2020).", "email": "Yuanchang_Xie@uml.edu", "phone": "978-934-3681", "url": "https://www.uml.edu/engineering/civil-environmental/faculty-staff-students/faculty/xie-yuanchang.aspx"},
    ],
    "affiliated": [
        {"name": "Alkim Akyurtlu", "photo": "akyurtlu", "title": "Professor, Electrical and Computer Engineering; Director, Raytheon UMass Lowell Research Institute (RURI); Director, Printed Electronics Research Collaborative (PERC)",
         "areas": "Additive manufacturing and printed electronics for RF and microwave devices, wearables, functional printable inks, metamaterials",
         "note": "PI of BOND-AI, the NextFlex award on physics-informed reliability qualification for high-temperature printed interfaces, with the director as Co-PI.", "email": "Alkim_Akyurtlu@uml.edu", "phone": "978-934-3336", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/akyurtlu-alkim.aspx"},
        {"name": "Yu Cao", "photo": "cao", "title": "Professor, Miner School of Computer and Information Sciences; Director, UMass Center for Digital Health",
         "areas": "Medical imaging, multimodal deep learning, computer vision, AI, digital health", "email": "yu_cao@uml.edu", "phone": "978-934-3628", "url": "https://www.uml.edu/sciences/computer-science/people/cao-yu.aspx"},
        {"name": "Supriya Chakrabarti", "photo": "chakrabarti", "title": "Professor, Physics and Applied Physics; Director, Lowell Center for Space Science and Technology (LoCSST)",
         "areas": "Space experiments and instrumentation, hyperspectral imaging from the UV to the near infrared, lidar, exoplanets and planetary atmospheres", "email": "Supriya_Chakrabarti@uml.edu", "phone": "978-934-3287",
         "url": "https://www.uml.edu/research/locsst/about/faculty-staff/chakrabarti-supriya.aspx"},
        {"name": "Chunxiao (Tricia) Chigan", "photo": "chigan", "title": "Professor, Electrical and Computer Engineering",
         "areas": "Communication networks and network security", "email": "Tricia_Chigan@uml.edu", "phone": "978-934-3364", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/chigan-tricia.aspx"},
        {"name": "Hsien-Yuan (Mark) Hsu", "photo": "hsu", "title": "Associate Professor, School of Education, College of Fine Arts, Humanities and Social Sciences",
         "areas": "Multilevel modeling, psychometrics, and engineering education; education research and evaluation for the center's training programs",
         "note": "Education and workforce lead; Co-PI with Tseng on the NSF cyberinfrastructure planning award (#2609490).",
         "email": "HsienYuan_Hsu@uml.edu", "phone": "978-934-4608", "url": "https://www.uml.edu/education/faculty-staff/faculty/hsu-hsien-yuan.aspx"},
        {"name": "Murat Inalpolat", "photo": "inalpolat", "title": "Professor, Mechanical and Industrial Engineering; Associate Chair for Doctoral Studies",
         "areas": "Structural health monitoring, diagnostics and prognostics, structural dynamics, vibrations, acoustics, signal processing", "email": "Murat_Inalpolat@uml.edu", "phone": "978-934-2556", "url": "https://www.uml.edu/engineering/mechanical-industrial/faculty/inalpolat-murat.aspx"},
        {"name": "Christopher Niezrecki", "photo": "niezrecki", "title": "Distinguished University Professor, Mechanical and Industrial Engineering; Director, Center for Energy Innovation; Co-director, Rist Institute for Sustainability and Energy",
         "areas": "Renewable energy systems, wind turbine dynamics, structural health monitoring and inspection, structural dynamics and acoustics, smart materials", "email": "Christopher_Niezrecki@uml.edu", "phone": "978-934-2963", "url": "https://www.uml.edu/engineering/mechanical-industrial/faculty/niezrecki-christopher.aspx"},
        {"name": "Sheree A. Pagsuyoin", "photo": "pagsuyoin", "title": "Professor, Civil and Environmental Engineering",
         "areas": "Environmental fate of emerging contaminants, wastewater-based epidemiology, low-cost water treatment, environmental systems modeling",
         "note": "Collaborator on machine learning for wastewater-based public health risk monitoring; NSF CAREER awardee.",
         "email": "Sheree_Pagsuyoin@uml.edu", "phone": "978-934-5976",
         "url": "https://www.uml.edu/engineering/civil-environmental/faculty-staff-students/faculty/pagsuyoin-sheree.aspx"},
        {"name": "Oshadha Ranasingha", "photo": "ranasingha", "title": "Assistant Professor, Electrical and Computer Engineering; PERC and RURI",
         "areas": "Functional inks for printed electronics and additive manufacturing, fully printed micro-supercapacitors, energy harvesting, hardware authentication",
         "note": "Co-PI on BOND-AI, the NextFlex award on high-temperature printed interfaces and bond joints.", "email": "oshadha_ranasingha@uml.edu", "phone": "978-934-2336", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/ranasingha-oshadha.aspx"},
        {"name": "Hengyong Yu", "photo": "yu", "title": "Professor, Electrical and Computer Engineering",
         "areas": "Biomedical imaging, medical image reconstruction, image processing and analysis", "email": "Hengyong_Yu@uml.edu", "phone": "978-934-6756", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/yu-hengyong.aspx"},
    ],
    "external": [
        {"name": "Heidi Dempsey", "tag": "External collaborator", "photo": "dempsey", "inst": None, "title": "Research Director of the Northeast US, Red Hat",
         "areas": "Grows research and open-source collaborations between Red Hat and academic partners; Red Hat partner for the center's Friendly Fedora and Podman work",
         "email": "hdempsey@redhat.com", "phone": "", "url": "https://www.bu.edu/hic/profile/heidi-dempsey/"},
        {"name": "Babu Jain", "tag": "External collaborator", "photo": "jain", "inst": None, "title": "Founder and CEO, Navia Energy Inc.", "areas": "AI-driven renewable energy systems; industry partner on the center's resilient smart grids project",
         "email": "babu.jain@naviaenergy.com", "phone": "", "url": "https://www.linkedin.com/in/babu-jain-188470/"},
        {"name": "Martin Margala", "photo": "margala", "title": "Professor and Director, School of Computing and Informatics, University of Louisiana at Lafayette",
         "areas": "Reconfigurable and secure architectures, energy-efficient and reliable systems, design for testability",
         "note": "Co-founder and founding co-director of the center, October 2019 to July 2021, while Professor and Chair of Electrical and Computer Engineering at UMass Lowell.",
         "email": "martin.margala@louisiana.edu", "tag": "External collaborator",
         "url": "https://sciences.louisiana.edu/node/492", "inst": "Louisiana"},
        {"name": "Anurag Srivastava", "tag": "External collaborator", "photo": "srivastava", "inst": "West Virginia", "title": "Raymond J. Lane Professor and Chairperson, Lane Department of Computer Science and Electrical Engineering, West Virginia University; IEEE Fellow",
         "areas": "Data-driven algorithms for power system operation, control, and resilience; WVU partner on the SUMMIT federated smart grid testbed",
         "email": "anurag.srivastava@mail.wvu.edu", "phone": "", "url": "https://directory.statler.wvu.edu/faculty-staff-directory/anurag-srivastava"},
    ],
    "collaborators": [
        {"name": "NYU Tandon School of Engineering", "org": "SUMMIT federation site", "note": "Second node of the multi-site smart grid testbed, led by center member Yuzhang Lin"},
        {"name": "West Virginia University", "org": "SUMMIT federation site", "note": "Third node of the multi-site smart grid testbed"},
        {"name": "UMass Lowell Applied Research Corporation (UMLARC)", "org": "Defense and state applied research", "note": "Place of performance for the ARPO projects"},
        {"name": "Navia Energy Inc.", "org": "Industry partner", "note": "Resilient smart grid research"},
        {"name": "Red Hat Inc.", "org": "Industry partner", "note": "Open-source systems research"},
        {"name": "Massachusetts Technology Collaborative", "org": "State partner", "note": "Applied AI Models program"},
    ],
}

# ---------------------------------------------------------------- projects
PROJECTS = [
    {"tag": "New in 2026", "sponsor": "National Science Foundation, Major Research Instrumentation Track 2 (Award #2511635)",
     "role": "PI", "title": "SUMMIT: A Secure and Resilient Multi-site Smart Grid Testbed for Multidisciplinary Research and Training",
     "amount": "$2.0M", "share": "UMass Lowell share $1.56M", "period": "Oct 2026 to Sep 2029",
     "team": "PI Vinod Vokkarane; Co-PIs Orlando Arias and Lewis Tseng (UMass Lowell), Yuzhang Lin (NYU), and Anurag Srivastava (WVU); senior personnel Yan Luo, Seung Woo Son, and Christopher Niezrecki",
     "desc": ("A federated cyber-physical testbed that links RTDS real-time simulation of the Northeast transmission grid with control, "
              "networking, and cybersecurity hardware in the loop across three universities over a wide-area SDN, delivered as "
              "HIL Simulation-as-a-Service. A postdoctoral researcher will lead federation development."),
     "domain": "Energy"},
    {"tag": "New in 2026", "sponsor": "Massachusetts Technology Collaborative, Applied AI Models program",
     "role": "PI", "title": "ARPO-Sensor Fusion: Autonomous Robotic Planning and Optimization for Intelligence Sensor Fusion",
     "amount": "$625K", "share": "$500K direct plus $125K cost share; UMass Lowell and UMLARC share $247K", "period": "Oct 2026 to Sep 2027",
     "team": "PI Vinod Vokkarane; performed at UMLARC",
     "desc": "Applied AI models that fuse multi-sensor intelligence feeds to plan and optimize autonomous robotic missions.",
     "domain": "Autonomy"},
    {"tag": "New in 2026", "sponsor": "NextFlex (FlexTech Alliance)", "role": "Co-PI",
     "title": "BOND-AI: A Standardized Reliability Qualification Methodology for High-Temperature Printed Interfaces and Bond Joints, Enabled by Physics-Informed AI, on a 500 \u00b0C-Capable Alumina Platform",
     "amount": "$1.0M", "share": "$500K direct plus $500K cost share", "period": "Oct 2026, 12 months",
     "team": "PI Alkim Akyurtlu (Director, RURI and PERC); Co-PIs Vinod Vokkarane, Oshadha Ranasingha, and Scott Stapleton; with Applied Nanotech, Bayflex Solutions, RAGE Systems, and RTX",
     "desc": "A qualification methodology for printed interfaces and bond joints that must survive 500 \u00b0C, using physics-informed AI to predict reliability rather than test it one sample at a time.",
     "url": "https://bondai-portal.onrender.com/", "link": "Project portal",
     "domain": "Printed electronics"},
    {"tag": "New in 2026", "sponsor": "U.S. Army",
     "role": "PI", "title": "ARPO: Autonomous Robotic Planning and Optimization",
     "amount": "$225K", "period": "Mar 2026 to Jul 2027",
     "team": "PI Vinod Vokkarane; UMLARC and UMass Lowell",
     "desc": "Planning and optimization methods for autonomous robotic systems operating over contested tactical networks.",
     "domain": "Autonomy"},
    {"tag": "Completed", "sponsor": "Office of Naval Research",
     "role": "PI", "title": "Unified Post-Disaster Restoration Planning for Cyber-Physical Power Distribution Systems",
     "amount": "$550K", "period": "Jan 2024 to Oct 2025",
     "team": "PI Vinod Vokkarane; Co-PIs Orlando Arias (UMass Lowell), Yuzhang Lin (NYU)",
     "desc": ("Joint restoration of the power and communication layers of a distribution grid after a disaster, "
              "including networked microgrid formation and communication-aware state recovery."),
     "domain": "Energy"},
    {"tag": "Active", "sponsor": "U.S. Department of Energy",
     "role": "PI (UMass Lowell)", "title": "CyberCARED: Northeast University Cybersecurity Center for Advanced and Resilient Energy Delivery",
     "amount": "$3.5M", "share": "consortium total; UMass Lowell share $150K", "period": "Oct 2024 to Sep 2027",
     "team": "UMass Lowell PI Vinod Vokkarane; multi-university consortium",
     "desc": "A regional university center on cybersecurity for energy delivery systems, combining research with workforce training.",
     "domain": "Energy"},
    {"tag": "Active", "sponsor": "Commonwealth of Massachusetts, Healey-Driscoll Administration",
     "title": "Massachusetts Advanced Nuclear and Fusion Energy Roadmaps",
     "amount": "", "period": "Oct 2025 to 2026",
     "team": "Lead: Sukesh Aghara, with UMass Lowell's Rist Institute for Sustainability and Energy",
     "desc": "A statewide assessment, commissioned by Gov. Healey, of what Massachusetts would need to lead in advanced nuclear and fusion energy: stakeholder engagement across utilities, regulators, industry, labor, and communities, a public discussion series, and recommendations on workforce, regional coordination, and research capacity.",
     "domain": "Energy"},
    {"tag": "Active", "sponsor": "International Atomic Energy Agency",
     "title": "Intercontinental Nuclear Institute (INI)",
     "amount": "", "period": "Ongoing",
     "team": "Co-director: Sukesh Aghara",
     "desc": "An IAEA-funded international training program in nuclear technology, security, and safeguards for early-career professionals, run with partner institutions.",
     "domain": "Nuclear"},
    {"tag": "Active", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Advanced Technologies and Data Analytics for Safe, Smart, and Efficient Transportation (ASSET)",
     "amount": "$604K", "period": "Apr 2025 to Dec 2026", "team": "PI Yuanchang Xie",
     "desc": "Advanced technologies and data analytics for safer and more efficient transportation in Massachusetts.", "domain": "Transportation"},
    {"tag": "Active", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "A Railroad Trespassing Detection and Dynamic Warning System Based on Artificial Intelligence and Edge Computing",
     "amount": "$750K", "period": "Sept 2024 to Sept 2026", "team": "PI Yuanchang Xie",
     "desc": "AI and edge computing to detect railroad trespassing and warn in real time.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "U.S. Department of Transportation, SMART program, through the New Hampshire Department of Transportation", "role": "UMass Lowell PI",
     "title": "Moving Towards a Smart, Connected, and Interoperable Traffic Monitoring System by Retrofitting Existing Infrastructure",
     "amount": "$180K", "period": "Mar 2025 to Mar 2026", "team": "UMass Lowell PI Yuanchang Xie",
     "desc": "Retrofitting existing infrastructure into a connected, interoperable traffic monitoring system.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Calibration of Safety Performance Functions for Highway Ramp Terminals in Massachusetts",
     "amount": "$277K", "period": "Sept 2022 to Sept 2023", "team": "PI Yuanchang Xie",
     "desc": "Safety performance functions calibrated for Massachusetts ramp terminals.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "New England Transportation Consortium", "role": "PI",
     "title": "Current Status of Transportation Data Analytics and a Pilot Case Study Using Artificial Intelligence",
     "amount": "$200K", "period": "May 2021 to Dec 2023", "team": "PI Yuanchang Xie",
     "desc": "The state of transportation data analytics across New England, with an AI pilot study.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "Co-PI",
     "title": "Multisource Data Fusion for Accurate Traffic Incident Detection",
     "amount": "$150K", "period": "Apr 2021 to Apr 2023", "team": "Co-PI Yuanchang Xie",
     "desc": "Fusing data sources to detect traffic incidents accurately.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Developing Massachusetts-Specific Trip Generation Models for Land Use Projects",
     "amount": "$150K", "period": "Mar 2021 to May 2023", "team": "PI Yuanchang Xie",
     "desc": "Trip generation models built for Massachusetts land use projects.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Uncovering the Root Causes of Truck Rollover Crashes on Ramps",
     "amount": "$120K", "period": "Apr 2021 to Mar 2023", "team": "PI Yuanchang Xie",
     "desc": "Root causes of truck rollover crashes on highway ramps.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "Co-PI",
     "title": "A UAS Network for Transportation Emergency Response",
     "amount": "$60K", "period": "Mar 2021 to July 2022", "team": "Co-PI Yuanchang Xie",
     "desc": "Unmanned aircraft systems networked for transportation emergency response.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "U.S. Army Combat Capabilities Development Command, Soldier Center", "role": "Co-PI",
     "title": "Drone-Based Infrared Wireless Sensor Network for Multimodal Underground Situational Awareness",
     "amount": "$956K", "period": "Sept 2020 to Sept 2023", "team": "Co-PI Yuanchang Xie",
     "desc": "Drone-carried infrared sensor networks for situational awareness underground.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Recalibration of Safety Performance Functions for Urban Intersections in Massachusetts",
     "amount": "$107K", "period": "Sept 2019 to June 2021", "team": "PI Yuanchang Xie",
     "desc": "Safety performance functions recalibrated for urban intersections in Massachusetts.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Collecting Model Inventory of Roadway Elements (MIRE) Fundamental Data Elements for Intersections in Massachusetts",
     "amount": "$148K", "period": "Jan 2019 to June 2023", "team": "PI Yuanchang Xie",
     "desc": "MIRE fundamental data elements collected for Massachusetts intersections.", "domain": "Transportation"},
    {"tag": "Active", "sponsor": "U.S. Department of Transportation, ATCMTD, through MaineDOT", "role": "UMass Lowell PI",
     "title": "Maine Advanced Signal Control and Connected Vehicle System for Safe, Efficient and Equitable Rural Transportation (MAST)",
     "amount": "$150K", "period": "Nov 2023 to Dec 2026",
     "team": "UMass Lowell PI Yuanchang Xie",
     "desc": "Advanced signal control and connected vehicle systems for rural transportation in Maine.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Railroad Grade Crossing Profile Data Collection and Modeling",
     "amount": "$353K", "period": "Oct 2023 to Aug 2025",
     "team": "PI Yuanchang Xie",
     "desc": "Collecting and modeling grade crossing profiles across the Commonwealth to support safety analysis.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "PI",
     "title": "Smart Work Zone Control and Performance Evaluation Based on Trajectory Data",
     "amount": "$150K", "period": "Apr 2022 to Sept 2023",
     "team": "PI Yuanchang Xie",
     "desc": "Work zone control and performance evaluation driven by vehicle trajectory data.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "Massachusetts Department of Transportation", "role": "UMass Lowell PI",
     "title": "Artificial Intelligence Framework for Crosswalk Detection across Massachusetts",
     "amount": "$47K", "period": "May 2023 to Feb 2024",
     "team": "UMass Lowell PI Yuanchang Xie",
     "desc": "Statewide crosswalk inventory and condition assessment from aerial imagery using deep learning.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "National Science Foundation", "role": "Co-PI",
     "title": "Collaborative Research: Understanding the Impacts of Automated Vehicles on Traffic Flow Using Empirical Data",
     "amount": "$182K", "period": "Mar 2019 to Feb 2023",
     "team": "Co-PI Yuanchang Xie",
     "desc": "Empirical study of how automated vehicles change traffic flow in mixed traffic.", "domain": "Transportation"},
    {"tag": "Completed", "sponsor": "National Science Foundation", "role": "PI",
     "title": "Ethical Algorithms in Autonomous Vehicles",
     "amount": "$557K", "period": "July 2017 to June 2022",
     "team": "PI Nicholas Evans; Co-PI Yuanchang Xie; with Heidi Furey",
     "desc": "The ethics of decision algorithms in autonomous vehicles, joining the center's transportation and ethics work.", "domain": "Transportation"},
    {"tag": "Active", "sponsor": "National Science Foundation, OAC Category III (Award #2609490)",
     "role": "PI", "title": "Planning Federated AI-Ready Cyberinfrastructure for Advanced Microscopy and Imaging: A Teach-Explore-Design Framework for Community-Driven Infrastructure",
     "amount": "$499K", "period": "Aug 2026 onward",
     "team": "PI Lewis Tseng; Co-PIs Hsien-Yuan Hsu (UMass Lowell) and Yu-Tsun Shao (University of Southern California)",
     "desc": "Planning a federated, AI-ready cyberinfrastructure for advanced microscopy and imaging, designed with the community that will use it.", "domain": "Distributed systems"},
    {"tag": "Active", "sponsor": "National Science Foundation, CNS CAREER (Award #2449640)",
     "role": "PI", "title": "Towards Fault-tolerant Edge Computing for Cyber-Physical Systems: Distributed Primitives for Coordination under Cyber Attacks",
     "amount": "$342K", "period": "Sept 2024 onward",
     "team": "PI Lewis Tseng",
     "desc": "Coordination primitives that keep an edge cluster correct and fast enough for a control loop while under attack.", "domain": "Distributed systems"},
    {"tag": "Active", "sponsor": "National Science Foundation, OAC Core (Award #2312982)",
     "role": "Co-PI", "title": "Improving Data Integrity for HPC Datasets using Sparsity Profile",
     "amount": "$600K", "period": "June 2023 onward",
     "team": "PI Seung Woo Son; Co-PI Orlando Arias",
     "desc": "Detecting and correcting corruption in high-performance computing datasets using their sparsity structure.", "domain": "HPC"},
    {"tag": "Completed", "sponsor": "National Science Foundation, CAREER (Award #1751143)",
     "role": "PI", "title": "Reliable and Efficient Data Encoding for Extreme-Scale Simulation and Analysis",
     "amount": "$500K", "period": "Apr 2018 to 2024",
     "team": "PI Seung Woo Son",
     "desc": "Encoding schemes that keep simulation data usable and verifiable at extreme scale.", "domain": "HPC"},
    {"tag": "Completed", "sponsor": "Office of Naval Research",
     "role": "PI", "title": "Software-Defined Cyber-Physical Microgrids (SDCPM) for Agile Adaptation to High-Impact, Low-Probability Disturbances",
     "amount": "$300K", "period": "2021 to 2024",
     "team": "PI Vinod Vokkarane",
     "desc": "Software-defined control of cyber-physical microgrids so they can reconfigure quickly around rare, high-impact disturbances.",
     "domain": "Energy"},
    {"tag": "Completed", "sponsor": "National Science Foundation, CNS Core",
     "role": "PI", "title": "Flexible Spectrum Allocation in Next-Generation Optical Networks",
     "amount": "$350K", "share": "plus a $16K REU supplement", "period": "2020 to 2024",
     "team": "PI Vinod Vokkarane",
     "desc": "Spectrum allocation algorithms for elastic optical networks, the line of work that led to the FUSION simulator.",
     "domain": "Networks"},
    {"tag": "Completed", "sponsor": "Office of Naval Research",
     "role": "Co-PI", "title": "Resilient Sensing and Communication Architecture for Naval Energy Infrastructure Monitoring",
     "amount": "$360K", "period": "2020 to 2023",
     "team": "PI Yuzhang Lin; Co-PI Vinod Vokkarane",
     "desc": "Cross-domain design of sensing and communication for resilient monitoring of naval energy infrastructure.",
     "domain": "Energy"},
    {"tag": "Active", "sponsor": "Red Hat Inc.",
     "title": "Open-Source Research: Friendly Fedora and Podman",
     "amount": "$200K+", "period": "2021 onward",
     "team": "PI Vinod Vokkarane",
     "desc": "Industry support for open-source systems research in the center, including the Friendly Fedora and Podman projects and the FUSION optical network simulation framework.",
     "domain": "Networks"},
    {"tag": "Active", "sponsor": "Navia Energy Inc.",
     "title": "Resilient Smart Grids",
     "amount": "", "period": "2024 to 2026",
     "team": "PI Vinod Vokkarane",
     "desc": "Industry-sponsored work on resilient operation of smart distribution grids.",
     "domain": "Energy"},
]

TOOLS = [
    {"name": "FUSION", "art": "fusion", "what": "Open-source benchmarking and simulation framework for reproducible optical network research (routing, spectrum and space assignment, QoT models). Described in JOCN, Sept. 2026.", "url": "https://github.com/SDNNetSim/FUSION", "link": "Source code on GitHub"},
    {"name": "Containerized grid co-simulation testbed", "art": "cosim", "what": "Docker-packaged HELICS, GridLAB-D, and ns-3 federation for cyber-physical power studies on the IEEE 123-bus feeder, with DNP3 traffic between control center and devices.", "url": "research-grid.html", "link": "Smart grid thrust"},
    {"name": "SUMMIT (in development)", "art": "summit_tool", "what": "Three-site federated smart grid testbed built around RTDS real-time simulators and a wide-area SDN, funded by the NSF MRI award and opening in 2026-2027 to collaborators as HIL Simulation-as-a-Service.", "url": "summit.html", "link": "SUMMIT project page"},
]

# ---------------------------------------------------------------- publications
# fields: year, authors (list), title, venue, details, doi, type (journal|conference), faculty (list), area
P = []
def pub(year, authors, title, venue, details, doi, typ, faculty, area, url=None):
    P.append(dict(year=year, authors=authors, title=title, venue=venue, details=details, doi=doi, type=typ, faculty=faculty, area=area, url=url))

# --- 2026
pub(2026, ["A. Rezaee","F. Arpanaei","R. McCann","H. Rabbani","J. A. Hernández","M. Brandt-Pearce","V. M. Vokkarane"],
    "QoT-Aware Dynamic Resource Allocation and Grooming in Multi-Band Space-Division Multiplexing Networks",
    "IEEE/Optica Journal of Optical Communications and Networking", "vol. 18, no. 10, Oct. 2026",
    "10.1364/JOCN.596435", "journal", ["Vokkarane"], "Optical networks")
pub(2026, ["A. Rezaee","R. McCann","V. M. Vokkarane"],
    "FUSION: A Unified Benchmarking Framework for Reproducible Optical Network Research",
    "IEEE/Optica Journal of Optical Communications and Networking", "vol. 18, no. 9, pp. D90-D105, Sept. 2026 (Special Issue on Benchmarking in Optical Networks)",
    "10.1364/JOCN.593123", "journal", ["Vokkarane"], "Optical networks")
pub(2026, ["A. Rezaee","F. Arpanaei","R. McCann","L. Nadal","J. A. Hernández","V. M. Vokkarane"],
    "QoT-Aware Spectral and Spatial Scaling Trade-offs in Multi-Band Space Division Multiplexing over EONs [Invited]",
    "IEEE/Optica Journal of Optical Communications and Networking", "vol. 18, no. 8, pp. C160-C172, Aug. 2026",
    "10.1364/JOCN.596854", "journal", ["Vokkarane"], "Optical networks")
pub(2026, ["M. Z. Islam","Y. Lin","V. M. Vokkarane"],
    "Disaster-Resilient Cyber-Physical Distribution System Reconfiguration and Dynamic Networked Microgrid Formation Under Intermittent Generation",
    "IEEE Transactions on Industry Applications", "vol. 62, no. 2, pp. 3459-3471, Mar. 2026",
    "10.1109/TIA.2025.3625866", "journal", ["Vokkarane","Lin"], "Smart grid")
pub(2026, ["H. Rabbani","A. Rezaee","H. Rabbani","V. M. Vokkarane","M. Brandt-Pearce"],
    "Experimental Determination of Filter Bandwidth Requirements for Coherent Pluggable Transceivers in Optical Data Center Networks",
    "IEEE International Conference on High Performance Switching and Routing (HPSR)", "pp. 1-5, June 2026",
    "10.1109/HPSR68369.2026.11615178", "conference", ["Vokkarane"], "Optical networks")
pub(2026, ["L. Tseng"],
    "Timely Control for Quantum Cloud: Orchestrating Entanglement Under Decay",
    "3rd ACM SIGCOMM Workshop on Quantum Networks and Distributed Quantum Computing (QuNet), ACM SIGCOMM 2026", "pp. 32-34, Aug. 2026",
    "10.1145/3833409.3833443", "conference", ["Tseng"], "Distributed systems")
pub(2026, ["L. Tseng","N. Yazdani-Motlagh"],
    "Green, Trust-Minimizing, and Sybil-Resistant? Rethinking How Blockchains Agree from an Energy Perspective",
    "ACM Sustainability Week 2026", "pp. 139-143, June 2026",
    "10.1145/3765611.3815150", "conference", ["Tseng"], "Distributed systems")
pub(2026, ["L. Tseng","K. Neupane","L. Ambarapu","M. Aloqaily"],
    "NC-DHT: Designing DHT for Blockchain Systems: Robustness and Anonymity",
    "Cluster Computing", "vol. 29, no. 5, June 2026",
    "10.1007/s10586-026-06101-0", "journal", ["Tseng"], "Distributed systems")
pub(2026, ["L. Tseng","C. Siems","K. Neupane","M. Aloqaily"],
    "Timing is the New Attack: Blockchain Cannot Prevent Market Manipulation at the Boundary",
    "IEEE International Conference on Consumer Electronics (ICCE)", "pp. 1-6, Jan. 2026",
    "10.1109/ICCE67443.2026.11449682", "conference", ["Tseng"], "Distributed systems")

pub(2026, ["T. Korinek","S. Aghara","L. Annadevula","R. Skoda"],
    "Future of Central Heating of University Campus: Phasing in Clean Sustainable Alternatives",
    "Energy Reports", "vol. 15, art. 108954, June 2026",
    "10.1016/j.egyr.2025.108954", "journal", ["Aghara"], "Nuclear energy and security")

# --- 2025
pub(2025, ["L. Annadevula","S. K. Aghara","C. Gazze","K. Jarman","C. Norman"],
    "Modeling Detector Response Curves for a High-Fidelity Uranium Measurement for Use in Simulations",
    "Radiation Measurements", "vol. 180, art. 107332, Jan. 2025",
    "10.1016/j.radmeas.2024.107332", "journal", ["Aghara"], "Nuclear energy and security")
pub(2025, ["M. Z. Islam","Y. Lin","V. M. Vokkarane"],
    "Cyber Security Constrained Economic Dispatch for Resilient Power System Operation",
    "IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)", "pp. 1-6, Sept. 2025",
    "10.1109/SmartGridComm65349.2025.11204587", "conference", ["Vokkarane", "Lin"], "Smart grid")
pub(2025, ["M. Sasaninia","V. M. Vokkarane","Y. Lin","O. Arias"],
    "Exploring a Smart FDI Attack and Enhancing Anomaly Detection in Smart Meters",
    "IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)", "pp. 1-6, Sept. 2025",
    "10.1109/SmartGridComm65349.2025.11204616", "conference", ["Vokkarane","Arias","Lin"], "Smart grid")
pub(2025, ["F. Arpanaei","A. Rezaee","M. Ranjbar Zefreh","R. McCann","L. Nadal","J. M. Rivas-Moscoso","Ó. González de Dios","A. Sánchez-Macián","D. Larrabeiti","V. M. Vokkarane","J. A. Hernández"],
    "Best Planning Practices for Ultra-High-Capacity Networks Based on Multi-Band over Space Division Multiplexing",
    "European Conference on Optical Communication (ECOC)", "pp. 1-4, Sept. 2025",
    "10.1109/ECOC66593.2025.11263159", "conference", ["Vokkarane"], "Optical networks")
pub(2025, ["M. Choi","T. Azzaoui","K. Chaisson","O. Arias","S. W. Son"],
    "Detecting Silent Data Corruption from Hardware Counters",
    "IEEE International Conference on Cluster Computing (CLUSTER)", "pp. 1-13, Sept. 2025",
    "10.1109/CLUSTER59342.2025.11186479", "conference", ["Arias","Son"], "HPC and hardware")
pub(2025, ["Z. Sharifi Soltani","A. Rezaee","O. Arias","V. M. Vokkarane"],
    "QoS-Based Recovery in 6G Optical Transport Networks: A Fast Service Prioritization Approach",
    "International Conference on Transparent Optical Networks (ICTON)", "pp. 1-4, July 2025",
    "10.1109/ICTON67126.2025.11125465", "conference", ["Vokkarane","Arias"], "Optical networks")
pub(2025, ["A. Rezaee","F. Arpanaei","R. McCann","J. A. Hernández","V. M. Vokkarane"],
    "Rethinking Flexibility: When Fixed-Grid with Grooming Outperforms Flex-Grid in EONs",
    "International Conference on Transparent Optical Networks (ICTON)", "pp. 1-4, July 2025",
    "10.1109/ICTON67126.2025.11125074", "conference", ["Vokkarane"], "Optical networks")
pub(2025, ["H. Rabbani","A. Rezaee","F. Arpanaei","V. M. Vokkarane","M. Brandt-Pearce"],
    "Modeling Nonlinear Noise for Arbitrary Pulse Shapes in Optical Fiber Communication Systems",
    "International Conference on Transparent Optical Networks (ICTON)", "pp. 1-4, July 2025",
    "10.1109/ICTON67126.2025.11125454", "conference", ["Vokkarane"], "Optical networks")
pub(2025, ["A. Rezaee","R. McCann","V. M. Vokkarane"],
    "Learning to Slice: ML-Assisted Segmentation for Dynamic Resource Allocation in SDM-EONs",
    "IEEE International Conference on High Performance Switching and Routing (HPSR)", "pp. 1-3, May 2025",
    "10.1109/HPSR64165.2025.11038887", "conference", ["Vokkarane"], "Optical networks")
pub(2025, ["A. Rezaee","R. McCann","H. Rabbani","M. Brandt-Pearce","V. M. Vokkarane"],
    "ISRS-Enhanced PLI-Aware Routing for Multi-Band Elastic Optical Networks",
    "IEEE International Conference on High Performance Switching and Routing (HPSR)", "pp. 1-6, May 2025",
    "10.1109/HPSR64165.2025.11038893", "conference", ["Vokkarane"], "Optical networks")
pub(2025, ["A. Rezaee","F. Arpanaei","R. McCann","H. Rabbani","J. A. Hernández","M. Brandt-Pearce","V. M. Vokkarane"],
    "Channel-Based ICXT- and NLI-Aware Service Provisioning for Multi-Band Over SDM Systems",
    "International Conference on Optical Network Design and Modeling (ONDM)", "pp. 1-6, May 2025",
    "10.23919/ONDM65745.2025.11029337", "conference", ["Vokkarane"], "Optical networks")
pub(2025, ["M. Z. Islam","Y. Lin","V. M. Vokkarane","J. Ogle"],
    "Observability-Aware Resilient PMU Networking",
    "IEEE Transactions on Power Systems", "vol. 40, no. 1, pp. 218-230, Jan. 2025",
    "10.1109/TPWRS.2024.3387338", "journal", ["Vokkarane","Lin"], "Smart grid")
pub(2025, ["R. Dai","Z. Liu","O. Arias","X. Guo","T. Yavuz"],
    "Evaluating the Effectiveness of Hardware Trojan Detection Approaches at RTL",
    "IEEE International Symposium on Hardware Oriented Security and Trust (HOST)", "pp. 250-260, May 2025",
    "10.1109/HOST64725.2025.11050040", "conference", ["Arias"], "HPC and hardware")
pub(2025, ["Y. Jeong","A. Moon","E. Yu","S. W. Son"],
    "Lightweight Stream-Based On-Device Earthquake Detection: A Sparse Profile Analysis Approach",
    "IEEE International Conference on Big Data (BigData)", "pp. 4948-4953, Dec. 2025",
    "10.1109/BigData66926.2025.11401927", "conference", ["Son"], "HPC and hardware")
pub(2025, ["J. Yoon","A. Moon","S. W. Son"],
    "Earthquake False Alarm Detection Model Augmented with Sparse Profile Analysis",
    "IEEE International Geoscience and Remote Sensing Symposium (IGARSS)", "pp. 6078-6082, Aug. 2025",
    "10.1109/IGARSS55030.2025.11242817", "conference", ["Son"], "HPC and hardware")
pub(2025, ["L. Lebow","M. Dunkle","C. Siems","J. Zarnstorff","L. Tseng"],
    "Revisiting State Machine Replication in Practice: Lessons from Building an etcd-inspired System",
    "ACM Symposium on Cloud Computing (SoCC)", "pp. 456-463, Nov. 2025",
    "10.1145/3772052.3772246", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["L. Tseng","V. Dang","L. Shaban","W.-P. Tsai","M. Aloqaily"],
    "SEED: A Distributed Framework for Multi-Drone Search via Satellite-Edge-Enabled Drones",
    "IEEE Global Communications Conference (GLOBECOM)", "pp. 2958-2963, Dec. 2025",
    "10.1109/GLOBECOM59602.2025.11432647", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["V. Balasubramanian","L. Tseng"],
    "Content-Aware Gossip Protocol for Improving Access Latency in Mobile Device Cloud",
    "IEEE Global Communications Conference (GLOBECOM)", "pp. 5387-5392, Dec. 2025",
    "10.1109/GLOBECOM59602.2025.11432341", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["N. Yazdani Motlagh","K. Neupane","L. Tseng","H.-Y. Hsu"],
    "WIP: What Employers Want: A Data-Driven Analysis of Soft Skill Trends in Computer Science Job Postings (2012-2024)",
    "IEEE Frontiers in Education Conference (FIE)", "pp. 1-5, Nov. 2025",
    "10.1109/FIE63693.2025.11328524", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["V. Dang","L. Shaban","L. Tseng"],
    "Experience: Evaluating Real-Time Drone OS Under Extreme and Adversarial Environment",
    "IEEE/IFIP International Conference on Dependable Systems and Networks Workshops (DSN-W)", "pp. 240-241, June 2025",
    "10.1109/DSN-W65791.2025.00070", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["L. Tseng","Y.-T. Shao"],
    "Poster: Designing Scalable, Secure Systems for Atomic-Scale Physical AI: Enabling Open Science and Collaborative Data Management and Analytics",
    "IEEE/IFIP International Conference on Dependable Systems and Networks, Supplemental Volume (DSN-S)", "pp. 247-248, June 2025",
    "10.1109/DSN-S65789.2025.00070", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["L. Tseng"],
    "Poster: Agree to Disagree: Revisiting the Comparison of (Multi-)Paxos and Raft",
    "IEEE/IFIP International Conference on Dependable Systems and Networks, Supplemental Volume (DSN-S)", "pp. 249-250, June 2025",
    "10.1109/DSN-S65789.2025.00071", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["S.-W. Ho","K. Neupane","W.-P. Tsai","L. Tseng","M. Aloqaily"],
    "Deploying Digital Twins as a Service in Hybrid Clouds",
    "IEEE International Conference on Human-Machine Systems (ICHMS)", "May 2025",
    "10.1109/ICHMS65439.2025.11153976", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["K. Neupane","L. Tseng","M. Aloqaily"],
    "Consensus-driven Intrusion Detection Systems: Enhancing Performance and Fault-tolerance using Approximate Consensus",
    "Intelligent Cybersecurity Conference (ICSC)", "pp. 256-263, May 2025",
    "10.1109/ICSC65596.2025.11140282", "conference", ["Tseng"], "Distributed systems")
pub(2025, ["T. Bantikyan","J. Zarnstorff","T.-Y. Chou","L. Tseng","R. Palmieri"],
    "Pineapple: Unifying Multi-Paxos and Atomic Shared Registers",
    "USENIX Symposium on Networked Systems Design and Implementation (NSDI)", "Apr. 2025",
    None, "conference", ["Tseng"], "Distributed systems")

# order: year desc, journals first within year, then by title
# --- 2025-2026 papers of the wider center faculty (Crossref, vetted Sept. 2026)
pub(2026, ["C. Pozzi", "C. Ng", "S. Lyon", "Y. Luo", "C. Niezrecki", "M. Inalpolat"],
    "A Novel Distributed Sensor Network to Assess Wind Turbine Blade Acoustics for Structural Health Monitoring",
    "Wind Energy", "vol. 29, no. 10, Sept. 2026",
    "10.1002/we.70148", "journal", ["Inalpolat", "Niezrecki", "Luo"], "Structural dynamics and health monitoring")
pub(2026, ["X. Yan", "Z. Bhuyan", "J. Oke", "G. Wu", "Y. Xie"],
    "A two-stage detection and segmentation framework for pedestrian crosswalk inventory and condition assessment from aerial imagery",
    "Engineering Applications of Artificial Intelligence", "vol. 182, art. 115851, Oct. 2026",
    "10.1016/j.engappai.2026.115851", "journal", ["Xie"], "Transportation")
pub(2026, ["M. Zhu", "H. Yu", "Y. Chu"],
    "A two-stage tone mapping network based on attention mechanism for high dynamic range images",
    "Journal of Visual Communication and Image Representation", "vol. 115, art. 104672, Jan. 2026",
    "10.1016/j.jvcir.2025.104672", "journal", ["Yu"], "Medical imaging")
pub(2026, ["S. Han", "B. Morovati", "Y. Liu", "C. Fang", "S. Fan", "L. Zhou", "Y. Shi", "G. Wang", "H. Yu"],
    "Accelerated Physics-Guided Diffusion Model for 3-D Limited-Angle Reconstruction of Cardiac Computed Tomography",
    "IEEE Transactions on Radiation and Plasma Medical Sciences", "vol. 10, no. 7, pp. 1088-1098, Sept. 2026",
    "10.1109/trpms.2025.3650342", "journal", ["Yu"], "Medical imaging")
pub(2026, ["A. Moeinaddini", "T. Zhang", "C. D\u2019Agostino", "Y. Xie", "Y. Zou"],
    "Accounting for under-reporting in wildlife\u2013vehicle collision hotspot identification using copulas and Bayesian model averaging",
    "Accident Analysis & Prevention", "vol. 233, art. 108583, Aug. 2026",
    "10.1016/j.aap.2026.108583", "journal", ["Xie"], "Transportation")
pub(2026, ["S. Islam", "X. Ma", "C. Chigan"],
    "Adaptive Nonlinear Digital Self-Interference Cancellation for Full-Duplex Wireless Systems Using Hypernetwork-Based Incremental Learning",
    "IEEE Transactions on Machine Learning in Communications and Networking", "vol. 4, pp. 60-75, 2026",
    "10.1109/tmlcn.2025.3639365", "journal", ["Chigan"], "Wireless networks")
pub(2026, ["L. Unger", "A. Akyurtlu"],
    "Additively Manufactured Multilayer Fan-Out Interposer",
    "IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (AP-S/USNC-URSI)", "pp. 146-149, July 2026",
    "10.1109/ap-s/usnc-ursi60190.2026.11675622", "conference", ["Akyurtlu"], "Printed electronics")
pub(2026, ["G. C. Modak", "M. Cohn", "J. Allspaw", "H. Yanco", "C. Niezrecki", "A. Sabato"],
    "An integrated deep learning and virtual reality framework for automated, remote thermal inspection of buildings",
    "Health Monitoring of Structural and Biological Systems XX", "art. 32, Apr. 2026",
    "10.1117/12.3090803", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["X. Zhang", "S. Wang", "N. Liang", "Z. Zheng", "A. Cai", "L. Li", "H. Yu", "B. Yan"],
    "An interpretable cascaded residual iterative network for sparse-view spectral CT imaging",
    "Quantitative Imaging in Medicine and Surgery", "vol. 16, no. 3, pp. 203-203, Mar. 2026",
    "10.21037/qims-2025-1895", "journal", ["Yu"], "Medical imaging")
pub(2026, ["L. Zhou", "C. Fang", "B. Morovati", "S. Han", "S. Fan", "Y. shi", "H. Yu"],
    "CBCT-Pose: Few-Shot Viewpoint-Conditioned Diffusion for Sparse-View CBCT Reconstruction",
    "IEEE 23rd International Symposium on Biomedical Imaging (ISBI)", "pp. 1-5, Apr. 2026",
    "10.1109/isbi61048.2026.11515365", "conference", ["Yu"], "Medical imaging")
pub(2026, ["Y. Shi", "S. Fan", "C. Fang", "S. Han", "H. Li", "L. Zhou", "B. Morovati", "D. Wang", "H. Yu"],
    "Clinical Metadata-Guided Limited-Angle CT Image Reconstruction",
    "IEEE Transactions on Medical Imaging", "vol. 45, no. 7, pp. 3490-3504, July 2026",
    "10.1109/tmi.2026.3677586", "journal", ["Yu"], "Medical imaging")
pub(2026, ["L. Zhou", "B. Morovati", "D. Wang", "Y. Xu", "S. Han", "S. Fan", "C. Fang", "Y. Shi", "H. Yu"],
    "Co-Retention feature pyramid network for low-dose CT denoising via spatial and frequency domain learning",
    "Biomedical Signal Processing and Control", "vol. 123, art. 110584, Sept. 2026",
    "10.1016/j.bspc.2026.110584", "journal", ["Yu"], "Medical imaging")
pub(2026, ["V. Eniola", "J. Cimorelli", "X. Jin", "D. Willis", "C. Niezrecki"],
    "Co-optimization of costs and curtailment in hybrid wind-hydrogen powered microgrids: understanding the impact of overbuilding",
    "Energy Conversion and Management", "vol. 351, art. 121046, Mar. 2026",
    "10.1016/j.enconman.2026.121046", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["J. Cimorelli", "V. Eniola", "C. Niezrecki", "X. Jin", "D. Willis"],
    "Comparing the sizing and costs of wind versus solar energy generation for a compressed hydrogen energy storage remote microgrid",
    "Renewable Energy", "vol. 274, art. 126206, Oct. 2026",
    "10.1016/j.renene.2026.126206", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["C. Niezrecki"],
    "Coupling Wind and Solar Power Generation to Hydrogen Energy Storage",
    "World Congress on Civil, Structural, and Environmental Engineering", "Apr. 2026",
    "10.11159/iceptp26.004", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["H. Li", "S. Han", "H. Mao", "Y. Shi", "C. Fang", "J. Zhang", "W. Wu", "H. Yu"],
    "Cross-Distribution Diffusion Priors-Driven Iterative Reconstruction for Sparse-View CT",
    "IEEE Transactions on Medical Imaging", "vol. 45, no. 7, pp. 3878-3894, July 2026",
    "10.1109/tmi.2026.3687173", "journal", ["Yu"], "Medical imaging")
pub(2026, ["M. Huang", "S. Li", "Y. Lin", "K. Sun", "G. Sun", "Z. Wei"],
    "Data-driven linear state estimation for distribution systems with high penetration of photovoltaics",
    "Sustainable Energy, Grids and Networks", "vol. 47, art. 102345, Sept. 2026",
    "10.1016/j.segan.2026.102345", "journal", ["Lin"], "Smart grid")
pub(2026, ["M. Li", "C. Niu", "G. Wang", "M. R. Amma", "K. M. Chapagain", "S. Gabrielson", "A. Li", "K. Jonker", "N. de Ruiter", "J. A. Clark", "P. Butler", "A. Butler", "H. Yu"],
    "Deep Few-View High-Resolution Photon-Counting CT at Halved Dose for Extremity Imaging",
    "IEEE Transactions on Medical Imaging", "vol. 45, no. 3, pp. 1193-1207, Mar. 2026",
    "10.1109/tmi.2025.3618754", "journal", ["Yu"], "Medical imaging")
pub(2026, ["F. Bottalico", "J. S. Syed", "C. Niezrecki", "A. Sabato"],
    "Drone-based super-resolution imaging for automated wind turbine blade inspection",
    "Health Monitoring of Structural and Biological Systems XX", "art. 9, Apr. 2026",
    "10.1117/12.3086541", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["P. Wu", "R. Guo", "Z. Zhao", "J. Meng", "H. Yu"],
    "EEA-UNet: An efficient element-wise adaptive attention-based network for abdominal multi-organ segmentation",
    "Journal of X-Ray Science and Technology", "July 2026",
    "10.1177/08953996261462020", "journal", ["Yu"], "Medical imaging")
pub(2026, ["T. Zhang", "Y. Zou", "Y. Chen", "Y. Xie", "Y. Wang"],
    "Evaluating Personal Driving Risk and Road Safety in the Context of Road Navigation",
    "IEEE Transactions on Intelligent Transportation Systems", "vol. 27, no. 3, pp. 3021-3037, Mar. 2026",
    "10.1109/tits.2026.3652272", "journal", ["Xie"], "Transportation")
pub(2026, ["L. Han", "X. Zou", "Y. Huang", "H. Yu", "K. Xia", "H. Zhang"],
    "FMCS_YOLOV8m: A double-dimension anchor-free pulmonary nodule detection method that fuses multi-scale features",
    "Biomedical Signal Processing and Control", "vol. 118, art. 109797, June 2026",
    "10.1016/j.bspc.2026.109797", "journal", ["Yu"], "Medical imaging")
pub(2026, ["H. Huang", "A. Kumar", "Y. Lin"],
    "From Islanding Detection to Islanding Identification: A Critical Step Toward Self-Healing Distribution Networks With Grid-Forming Inverter Fleets",
    "IEEE Transactions on Smart Grid", "vol. 17, no. 4, pp. 3194-3206, July 2026",
    "10.1109/tsg.2026.3658159", "journal", ["Lin"], "Smart grid")
pub(2026, ["G. Wu", "X. Yan", "Y. Zou", "Y. Xie"],
    "From crash reports to safer roads: a multimodal framework integrating vision-language models and street view analysis",
    "Accident Analysis & Prevention", "vol. 228, art. 108419, Apr. 2026",
    "10.1016/j.aap.2026.108419", "journal", ["Xie"], "Transportation")
pub(2026, ["J. Sun", "D. Ke", "J. Xu", "Y. Lin"],
    "GNN-LSTM-Based Adaptive Discretization of PDEs in District Heating Networks Considering Multiple PV Scenarios",
    "IEEE PES International Meeting (PES IM)", "pp. 1-5, Jan. 2026",
    "10.1109/pesim67009.2026.11438494", "conference", ["Lin"], "Smart grid")
pub(2026, ["Y. Xu", "Y. Lin"],
    "GPU-Native Multi-Area State Estimation via SIMD Abstraction and Boundary Condensation",
    "ACM International Conference on Future and Sustainable Energy Systems (e-Energy)", "pp. 70-74, June 2026",
    "10.1145/3744255.3811735", "conference", ["Lin"], "Smart grid")
pub(2026, ["J. Xu", "G. Chen", "J. Lu", "Y. Lin"],
    "Graph Neural Networks with Diversity-Aware Neighbor Selection and Dynamic Multi-Scale Fusion for Multivariate Time Series Forecasting",
    "ICASSP 2026 - 2026 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)", "pp. 3431-3435, May 2026",
    "10.1109/icassp55912.2026.11461407", "conference", ["Lin"], "Smart grid")
pub(2026, ["A. Moeinaddini", "Y. Chen", "T. Zhang", "Y. Xie", "Y. Zou"],
    "Hybrid transformer and large language model framework for lane-level short-term travel time prediction",
    "Engineering Applications of Artificial Intelligence", "vol. 182, art. 115838, Oct. 2026",
    "10.1016/j.engappai.2026.115838", "journal", ["Xie"], "Transportation")
pub(2026, ["P. Wu", "X. Gao", "H. Yu"],
    "ISTNet: a multi-scale transformer-based architecture for malaria cell classification",
    "Medical & Biological Engineering & Computing", "vol. 64, no. 4, pp. 1423-1439, Feb. 2026",
    "10.1007/s11517-026-03538-8", "journal", ["Yu"], "Medical imaging")
pub(2026, ["J. Warrier", "H. Huang", "Y. Lin", "S. Q. Zhang"],
    "LARA: LLM-based Agile Power Distribution Network Restoration from Disastrous Events",
    "Findings of the Association for Computational Linguistics: EACL 2026", "pp. 6108-6116, 2026",
    "10.18653/v1/2026.findings-eacl.321", "conference", ["Lin"], "Smart grid")
pub(2026, ["H. Huang", "Y. Lin"],
    "Learning to Model the Dynamics of Black-Box Inverter-Based Resources With Multiple Unknown Control Modes From Noisy Measurement Data",
    "IEEE Transactions on Smart Grid", "vol. 17, no. 3, pp. 2530-2543, May 2026",
    "10.1109/tsg.2025.3647551", "journal", ["Lin"], "Smart grid")
pub(2026, ["P. Wu", "X. Ma", "Z. Zhao", "J. Zhang", "D. He", "Y. Zhang", "R. Guo", "H. Yu"],
    "MCEPANet: a connectivity-edge guided attention network for robust medical image segmentation with multi-scale boundary preservation",
    "Biomedical Physics & Engineering Express", "vol. 12, no. 4, art. 045020, July 2026",
    "10.1088/2057-1976/ae7c06", "journal", ["Yu"], "Medical imaging")
pub(2026, ["Z. Jia", "E. G. Holliday", "E. C. Tang", "H. B. Russo", "T. R. Rootes", "Y. Luo", "H. Yu", "D. Wang", "B. Zhang"],
    "Machine learning\u2013driven nanoparticle\u2013enhanced paper chromogenic array sensor approach for detecting sub-lethally injured Salmonella in low moisture food",
    "Food Research International", "vol. 229, art. 118523, Apr. 2026",
    "10.1016/j.foodres.2026.118523", "journal", ["Yu"], "Medical imaging")
pub(2026, ["M. Shahriar", "M. Z. Islam", "W. Zhang", "Y. Lin"],
    "Making Low-Voltage Networks Granularly Visible: Strategic Metering and Data-Driven Estimation via Graph Analytics and Learning",
    "ACM International Conference on Future and Sustainable Energy Systems (e-Energy)", "pp. 726-733, June 2026",
    "10.1145/3744255.3811721", "conference", ["Lin"], "Smart grid")
pub(2026, ["E. Lamport", "L. Unger", "S. G. R. Avuthu", "S. Chen", "J. Mapkar", "A. Akyurtlu"],
    "Materials and process optimizations for fabricating digital AM temperature and relative humidity sensor system circuits for use in high thermal stress environments",
    "Flexible and Printed Electronics", "vol. 11, no. 1, art. 015009, Feb. 2026",
    "10.1088/2058-8585/ae4528", "journal", ["Akyurtlu"], "Printed electronics")
pub(2026, ["X. Yan", "Y. Xie", "Z. Bhuyan", "B. Xiang", "G. Wu", "M. Shirazi"],
    "Merging behavior under varying work zone sign scenarios: A heterogeneity-based analysis",
    "Accident Analysis & Prevention", "vol. 235, art. 108614, Sept. 2026",
    "10.1016/j.aap.2026.108614", "journal", ["Xie"], "Transportation")
pub(2026, ["D. Bourzgui", "J. Shepard", "M. Inalpolat", "C. Niezrecki"],
    "Microturbine energy harvesting for acoustic-based wind turbine blade structural health monitoring",
    "Digital Twins, AI, and NDE for Industry Applications and Energy Systems 2026", "art. 19, Apr. 2026",
    "10.1117/12.3090465", "conference", ["Inalpolat", "Niezrecki"], "Structural dynamics and health monitoring")
pub(2026, ["W. Zhang", "Y. Lin", "M. Z. Islam", "H. Huang"],
    "Neuro-Physics Hybrid State Estimation of Distribution System With Smart Meter Voltage Measurements",
    "IEEE Transactions on Smart Grid", "vol. 17, no. 4, pp. 3546-3563, July 2026",
    "10.1109/tsg.2026.3658202", "journal", ["Lin"], "Smart grid")
pub(2026, ["H. A. Ahmad", "M. Civera", "C. Surace", "C. Niezrecki", "A. Sabato"],
    "Optical Motion Magnification for Vibration-based Condition Monitoring of Hydroelectric Turbines",
    "Computer Vision and SLDV for Structural Dynamics, 2026, Vol. 6", "pp. 85-94, 2026",
    "10.13052/rp-9788743814177a09", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["N. Sharma", "Y. Lin"],
    "Parameter Error Identification for Validation and Calibration of Dynamic Models of Inverter-Based Resources",
    "IEEE Transactions on Power Systems", "vol. 41, no. 1, pp. 396-412, Jan. 2026",
    "10.1109/tpwrs.2025.3596027", "journal", ["Lin"], "Smart grid")
pub(2026, ["J. Sun", "J. Xu", "Y. Lin", "D. Ke", "G. Chen"],
    "Planning distributed energy systems with low-grade heat sources integration: Geography-Based clustering and risk-informed thermal pipeline layout design approaches",
    "Energy", "vol. 344, art. 140004, Feb. 2026",
    "10.1016/j.energy.2026.140004", "journal", ["Lin"], "Smart grid")
pub(2026, ["F. Bottalico", "C. Niezrecki", "A. Sabato"],
    "Preliminary validation of a hybrid visual-inertial stereocamera calibration for 3D point tracking using independent UAVs",
    "Measurement", "vol. 264, art. 120287, Mar. 2026",
    "10.1016/j.measurement.2025.120287", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["P. Wu", "Z. Liu", "Z. Zhao", "R. Guo", "H. Yu"],
    "QLViT: ALightweight Cell ClassificationMethod forMicroscope Images Based on MViTv2 and Linear Attention",
    "Contemporary Mathematics", "pp. 593-612, Jan. 2026",
    "10.37256/cm.7120267713", "journal", ["Yu"], "Medical imaging")
pub(2026, ["S. Xu", "Y. Chen", "Y. Xie", "C. Wang"],
    "Quantifying the safety effects of left-turn signal control mode: A heterogeneous causal inference framework",
    "Accident Analysis & Prevention", "vol. 233, art. 108549, Aug. 2026",
    "10.1016/j.aap.2026.108549", "journal", ["Xie"], "Transportation")
pub(2026, ["C. Fang", "Y. Liu", "B. Morovati", "S. Han", "Y. Shi", "L. Zhou", "S. Fan", "H. Yu"],
    "ResPF: Residual Poisson Flow Generative Model for Efficient and Physically Consistent Sparse-View CT Reconstruction",
    "IEEE Transactions on Radiation and Plasma Medical Sciences", "vol. 10, no. 4, pp. 520-534, Apr. 2026",
    "10.1109/trpms.2025.3615836", "journal", ["Yu"], "Medical imaging")
pub(2026, ["M. Z. Islam", "Y. Yao", "Y. Lin", "S. Nahar Edib", "F. Ding"],
    "Risk-Aware Measurement Synchronization and Recovery for DSSE With Heterogeneous Data Sources",
    "IEEE Transactions on Instrumentation and Measurement", "vol. 75, pp. 9006215-9006215, 2026",
    "10.1109/tim.2026.3706155", "journal", ["Lin"], "Smart grid")
pub(2026, ["G. Chen", "Y. Lin"],
    "Robust State Estimation for Distribution Systems Based on Reinforcement-Learning-Assisted Memory-Augmented Deep Kalman Filter",
    "IEEE Transactions on Smart Grid", "pp. 1-1, 2026",
    "10.1109/tsg.2026.3711800", "journal", ["Lin"], "Smart grid")
pub(2026, ["B. Morovati", "S. Han", "C. Fang", "L. Zhou", "D. Wang", "S. Fan", "Y. Shi", "H. Yu"],
    "STABLE-PCCT: A Spectral Transformer Architecture with Bayesian Learning and Edge Preservation for Photon-Counting CT Image Reconstruction",
    "IEEE Transactions on Radiation and Plasma Medical Sciences", "pp. 1-1, 2026",
    "10.1109/trpms.2026.3676708", "journal", ["Yu"], "Medical imaging")
pub(2026, ["S. Lyon", "C. A. Ng", "C. Pozzi", "M. Inalpolat", "C. Niezrecki", "Y. Luo"],
    "Signal Strength and Network Performance Optimization of a Wireless Acoustic Sensor for Wind Turbine Blade Health Monitoring",
    "IEEE Sensors Journal", "vol. 26, no. 3, pp. 5195-5203, Feb. 2026",
    "10.1109/jsen.2025.3647370", "journal", ["Inalpolat", "Niezrecki", "Luo"], "Structural dynamics and health monitoring")
pub(2026, ["M. Z. Islam", "Y. Lin", "W. Zhang"],
    "Smart Meter Scheduling for Data-Driven Granular Customer Voltage Visibility",
    "IEEE Transactions on Smart Grid", "vol. 17, no. 1, pp. 832-844, Jan. 2026",
    "10.1109/tsg.2025.3624570", "journal", ["Lin"], "Smart grid")
pub(2026, ["J. Wang", "M. Li", "H. Fan", "Y. Chen", "Y. Yao", "Y. Liu", "Z. Wu", "Q. Du", "H. Yu", "J. Zheng"],
    "Sparse-View CT Reconstruction via Implicit Neural Representation Learning Powered by Dual-Domain Vision Foundation Models",
    "IEEE Transactions on Circuits and Systems for Video Technology", "vol. 36, no. 5, pp. 6108-6121, May 2026",
    "10.1109/tcsvt.2026.3655963", "journal", ["Yu"], "Medical imaging")
pub(2026, ["A. Seifelnasr", "X. A. Si", "M. Inalpolat", "J. Xi"],
    "Structural vibration and pulsatile flow enhance maxillary sinus ventilation: a combined experimental study and FEA modal analysis",
    "Journal of Biomechanics Open", "vol. 1, no. 1, art. 100006, June 2026",
    "10.1016/j.jbmo.2026.100006", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2026, ["R. Perkins", "B. Berkovich", "P. Robinette"],
    "The Cobra Effect in Trust Repair: Unintended Consequences of Rebuilding Trust in Human-Robot Collaboration",
    "Lecture Notes in Computer Science", "pp. 664-670, 2026",
    "10.1007/978-981-95-2382-5_57", "chapter", ["Robinette"], "Robotics and human-robot interaction")
pub(2026, ["F. Bottalico", "C. Niezrecki", "A. Sabato"],
    "Three-Dimensional Point Tracking Using UAV-Based Stereo Vision",
    "Computer Vision and SLDV for Structural Dynamics, 2026, Vol. 6", "pp. 1-8, 2026",
    "10.13052/rp-9788743814177a01", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2026, ["Z. Wu", "Y. Yang", "Y. Guo", "D. Wang", "T. Lyu", "Y. Xi", "Y. Chen", "H. Yu"],
    "UPMCL-Net: Unsupervised Projection-Domain Multiview Constraint Learning for CBCT Metal Artifact Reduction",
    "IEEE Transactions on Medical Imaging", "vol. 45, no. 5, pp. 1776-1786, May 2026",
    "10.1109/tmi.2025.3638630", "journal", ["Yu"], "Medical imaging")
pub(2026, ["C. Fang", "B. Morovati", "S. Han", "Y. Shi", "L. Zhou", "S. Fan", "D. Wang", "H. Yu"],
    "WDK-Net: Lightweight Wavelet Diffusion with Kolmogorov\u2013Arnold Network for Limited-angle Cardiac CT Reconstruction",
    "IEEE Transactions on Medical Imaging", "pp. 1-1, 2026",
    "10.1109/tmi.2026.3711942", "journal", ["Yu"], "Medical imaging")
pub(2025, ["J. Cimorelli", "V. Eniola", "C. Niezrecki", "X. Jin", "D. Willis"],
    "A Design and Optimization Tool for Sustainable Renewable\u2010Hydrogen Microgrid Systems",
    "International Journal of Energy Research", "vol. 2025, no. 1, Jan. 2025",
    "10.1155/er/3270718", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2025, ["B. Feng", "Y. Chu", "L. Zhou", "H. Yu"],
    "A Novel Game Graphics Quality Evaluation Model Using Saliency and Resolution Information",
    "IEEE International Conference on Image Processing (ICIP)", "pp. 1582-1587, Sept. 2025",
    "10.1109/icip55913.2025.11084690", "conference", ["Yu"], "Medical imaging")
pub(2025, ["T. N. Nagy", "Z. Rezaei Khavas", "M. R. Kotturu", "B. Liefooghe", "P. Robinette", "M. De Graaf"],
    "A Robot Should Compensate for Its Mistakes: An Exploration of the Dynamics of Trust Violation and Repair Strategies in Human-Robot Collaboration",
    "ACM Transactions on Human-Robot Interaction", "vol. 15, no. 1, pp. 1-34, Oct. 2025",
    "10.1145/3767729", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2025, ["P. Drane", "M. Inalpolat"],
    "A computational investigation into energy absorption characteristics of multicomponent facing-foam systems of helmets",
    "Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science", "vol. 239, no. 10, pp. 3867-3878, Jan. 2025",
    "10.1177/09544062251315017", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2025, ["E. T. Ozdemir", "M. Inalpolat", "H. K. Lee", "M. S. Kim"],
    "A generalized multibody dynamic model for dual-clutch transmissions with wet clutchsets",
    "Proceedings of the Institution of Mechanical Engineers, Part K: Journal of Multi-body Dynamics", "vol. 239, no. 3, pp. 254-273, June 2025",
    "10.1177/14644193251346325", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2025, ["D. B. Das", "O. Das", "M. Inalpolat"],
    "A multi-modal sensing based terrain identification approach for active lower limb exoskeletons",
    "Expert Systems with Applications", "vol. 275, art. 126862, May 2025",
    "10.1016/j.eswa.2025.126862", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2025, ["P. Wu", "P. An", "Z. Zhao", "R. Guo", "X. Ma", "Y. Qu", "Y. Xu", "H. Yu"],
    "A multi-stage training and deep supervision based segmentation approach for 3D abdominal multi-organ segmentation",
    "Journal of X-Ray Science and Technology", "vol. 33, no. 5, pp. 998-1011, July 2025",
    "10.1177/08953996251355806", "journal", ["Yu"], "Medical imaging")
pub(2025, ["C. Areias", "A. Luce", "E. Harper", "Y. Zhang", "A. Akyurtlu"],
    "Additive Integration of a Bare Die High-Power Microwave Amplifier Using 3-D Printed Interconnects",
    "IEEE Transactions on Microwave Theory and Techniques", "vol. 73, no. 10, pp. 7177-7187, Oct. 2025",
    "10.1109/tmtt.2025.3563113", "journal", ["Akyurtlu"], "Printed electronics")
pub(2025, ["C. Areias", "E. Harper", "Y. Zhang", "S. Trulli", "A. Akyurtlu"],
    "Additively Manufactured 3-D Printed Shielded Interconnects for Enhanced Immunity to EMI",
    "IEEE Transactions on Components, Packaging and Manufacturing Technology", "vol. 15, no. 12, pp. 2739-2749, Dec. 2025",
    "10.1109/tcpmt.2025.3628992", "journal", ["Akyurtlu"], "Printed electronics")
pub(2025, ["C. Areias", "A. Akyurtlu"],
    "An Examination of Aerosol Jet\u2010Printed Surface Roughness and its Impact on the Performance of High\u2010Frequency Electronics",
    "Advanced Engineering Materials", "vol. 27, no. 15, Mar. 2025",
    "10.1002/adem.202402715", "journal", ["Akyurtlu"], "Printed electronics")
pub(2025, ["R. Perkins", "P. Robinette"],
    "Beyond Scripted Apologies: Calibrating Trust with Dynamically Generated Responses",
    "34th IEEE International Conference on Robot and Human Interactive Communication (RO-MAN)", "pp. 2503-2509, Aug. 2025",
    "10.1109/ro-man63969.2025.11217702", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2025, ["L. Clark", "F. Ouchen", "L. Davidson", "O. Ranasingha", "E. Heckman", "C. Bartsch", "A. Mian"],
    "Characterization of Aerosol Jet-Printed Polyimide/h-BN Nanocomposite Thin Films for Space Applications",
    "The Minerals, Metals & Materials Series", "pp. 185-199, 2025",
    "10.1007/978-3-031-80748-0_16", "chapter", ["Ranasingha"], "Printed electronics")
pub(2025, ["S. Tang", "Y. Zou", "S. Wu", "Y. Xie", "Y. Zhang"],
    "Comparing Car-Following Behavior Patterns of Human-Driven Vehicles and Autonomous Vehicles in a Mixed Traffic Environment",
    "IEEE Transactions on Intelligent Transportation Systems", "vol. 26, no. 5, pp. 6814-6830, May 2025",
    "10.1109/tits.2025.3539757", "journal", ["Xie"], "Transportation")
pub(2025, ["", "S. Hamid", "C. Niezrecki", "A. Eberle"],
    "Contextualizing Wind Turbine Blade Waste: Comparison to Other Global Waste Streams",
    "SAMPE Journal", "vol. 61, no. 3, pp. 16-27, May 2025",
    "10.33599/sj.v61no3.02", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2025, ["Y. Xie", "C. Wang"],
    "Data analytics for safety applications",
    "Data Analytics for Intelligent Transportation Systems", "pp. 235-261, 2025",
    "10.1016/b978-0-443-13878-2.00014-x", "chapter", ["Xie"], "Transportation")
pub(2025, ["H. Yue", "W. Zhang", "Y. Lin", "H. Liu"],
    "Data-Centric Physics-Informed Graph Neural Networks for Ultra-Fast Power Flow Analysis",
    "IEEE Power &amp; Energy Society General Meeting (PESGM)", "pp. 1-5, July 2025",
    "10.1109/pesgm52009.2025.11225353", "conference", ["Lin"], "Smart grid")
pub(2025, ["H. Huang", "Y. Lin"],
    "Dynamic State Estimation for Power Systems With Uncertain Inputs",
    "IEEE Transactions on Instrumentation and Measurement", "vol. 74, pp. 1-13, 2025",
    "10.1109/tim.2025.3527495", "journal", ["Lin"], "Smart grid")
pub(2025, ["P. Wu", "Y. Qu", "Z. Zhao", "Z. Liu", "H. Yu"],
    "FQ-Conv-ViT: A quantized convolutional vision transformer model for diabetic retinopathy classification",
    "Signal, Image and Video Processing", "vol. 19, no. 8, May 2025",
    "10.1007/s11760-025-04254-w", "journal", ["Yu"], "Medical imaging")
pub(2025, ["N. D\u2019Agati", "C. Areias", "A. Luce", "A. Akyurtlu"],
    "Fully additive radio frequency front end system using vertical integration for circuit compaction <sup>*</sup>",
    "Flexible and Printed Electronics", "vol. 10, no. 4, art. 045014, Dec. 2025",
    "10.1088/2058-8585/ae2593", "journal", ["Akyurtlu"], "Printed electronics")
pub(2025, ["G. Chen", "Y. Lin"],
    "Gradient-Fused Multi-Step Deep Extended Kalman Filter for Forecasting Aided State Estimation in Distribution Systems",
    "IEEE Power &amp; Energy Society General Meeting (PESGM)", "pp. 1-5, July 2025",
    "10.1109/pesgm52009.2025.11225564", "conference", ["Lin"], "Smart grid")
pub(2025, ["Z. Liu", "P. Wu", "Z. Zhao", "H. Yu"],
    "ILViT: An Inception-Linear Attention-Based Lightweight Vision Transformer for Microscopic Cell Classification",
    "Journal of Imaging", "vol. 11, no. 7, art. 219, July 2025",
    "10.3390/jimaging11070219", "journal", ["Yu"], "Medical imaging")
pub(2025, ["B. Sarikaya", "E. Ozdemir", "M. Inalpolat", "H. K. Lee", "M. S. Kim"],
    "Influence of End\u2010Stop Design Variations on Dynamic Response of Centrifugal Pendulum Vibration Absorbers",
    "Shock and Vibration", "vol. 2025, no. 1, Jan. 2025",
    "10.1155/vib/6711505", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2025, ["G. J. Barlow", "D. Bagci Das", "O. Das", "S. E. Stapleton", "M. Inalpolat"],
    "Influence of helmet positioning on uncertainty of blunt impact absorption performance tests",
    "Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology", "vol. 240, no. 3, pp. 799-815, Mar. 2025",
    "10.1177/17543371251323411", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2025, ["M. Z. Islam", "Y. Ding", "Y. Tian", "T. Wang", "Y. Lin"],
    "Integration of Fiber Optic Sensing and Sparse Grid Sensors for Accurate Fault Localization in Power Distribution Networks",
    "IEEE Power &amp; Energy Society General Meeting (PESGM)", "pp. 1-5, July 2025",
    "10.1109/pesgm52009.2025.11225816", "conference", ["Lin"], "Smart grid")
pub(2025, ["V. Eniola", "J. Cimorelli", "C. Niezrecki", "D. Willis", "X. Jin"],
    "Investigating the impact of wind speed variability on optimal sizing of hybrid wind-hydrogen microgrids for reliable power supply",
    "International Journal of Hydrogen Energy", "vol. 106, pp. 834-849, Mar. 2025",
    "10.1016/j.ijhydene.2025.01.444", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2025, ["P. Wu", "Z. Liu", "Z. Zhao", "R. Guo", "H. Yu"],
    "LCPT: A lightweight cell classification method for microscope images based on vicinityViT and channel-position attention",
    "Signal, Image and Video Processing", "vol. 19, no. 14, Oct. 2025",
    "10.1007/s11760-025-04829-7", "journal", ["Yu"], "Medical imaging")
pub(2025, ["P. Christou", "M. Z. Islam", "Y. Lin", "J. Xiong"],
    "LLM4DistReconfig: A Fine-tuned Large Language Model for Power Distribution Network Reconfiguration",
    "Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)", "pp. 4136-4155, 2025",
    "10.18653/v1/2025.naacl-long.208", "conference", ["Lin"], "Smart grid")
pub(2025, ["E. Hedlund-Botti", "J. Schalkwyk", "N. Moorman", "C. Yang", "L. Seelam", "S. Waveren", "R. Perkins", "P. Robinette", "M. Gombolay"],
    "Learning Interpretable Features from Interventions",
    "Robotics: Science and Systems XXI", "June 2025",
    "10.15607/rss.2025.xxi.163", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2025, ["D. Wang", "F. L. Fan", "B. J. Hou", "H. Zhang", "Z. Jia", "B. Zhang", "R. Lai", "H. Yu", "F. Wang"],
    "Manifoldron: Direct Space Partition via Manifold Discovery",
    "IEEE Transactions on Neural Networks and Learning Systems", "vol. 36, no. 7, pp. 12311-12325, July 2025",
    "10.1109/tnnls.2024.3486252", "journal", ["Yu"], "Medical imaging")
pub(2025, ["E. Huynh", "P. Robinette"],
    "Modality Matters: A Sim-to-Real Study of Sonar-Based Object Detection and Tracking",
    "OCEANS 2025 - Great Lakes", "pp. 1-6, Sept. 2025",
    "10.23919/oceans59106.2025.11244929", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2025, ["S. Wu", "Y. Zhang", "Y. Zou", "Y. Xie", "Y. Wang"],
    "Modeling car\u2010following behaviors using a driving style\u2013based Bayesian model averaging Copula framework in mixed traffic flow",
    "Computer-Aided Civil and Infrastructure Engineering", "vol. 40, no. 21, pp. 3316-3332, Aug. 2025",
    "10.1111/mice.13514", "journal", ["Xie"], "Transportation")
pub(2025, ["Y. Chen", "Y. Zou", "J. Liu", "Y. Xie", "J. Tang"],
    "Modeling decision-making during unprotected left turns using interpretable deep learning and uncertainty quantification",
    "Accident Analysis & Prevention", "vol. 220, art. 108136, Sept. 2025",
    "10.1016/j.aap.2025.108136", "journal", ["Xie"], "Transportation")
pub(2025, ["A. Nickelson", "R. Perkins", "A. J. London", "P. Robinette", "K. Tumer"],
    "Multi-objective reinforcement learning framework for beneficent artificial intelligence",
    "Neural Computing and Applications", "vol. 37, no. 30, pp. 24773-24791, June 2025",
    "10.1007/s00521-025-11311-5", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2025, ["Y. Chen", "Y. Zou", "Y. Xie", "Y. Zhang", "J. Tang"],
    "Multimodal vehicle trajectory prediction based on intention inference with lane graph representation",
    "Expert Systems with Applications", "vol. 262, art. 125708, Mar. 2025",
    "10.1016/j.eswa.2024.125708", "journal", ["Xie"], "Transportation")
pub(2025, ["H. Huang", "Y. Lin"],
    "Neural Dynamic State Estimation and Prediction for Black-Box Inverter-Based Resources",
    "IEEE Power &amp; Energy Society General Meeting (PESGM)", "pp. 1-5, July 2025",
    "10.1109/pesgm52009.2025.11225334", "conference", ["Lin"], "Smart grid")
pub(2025, ["Z. Wu", "X. Zhong", "T. Lyu", "Y. Xi", "X. Ji", "Y. Zhang", "S. Xie", "H. Yu", "Y. Chen"],
    "PRAISE-Net: Deep Projection-Domain Data-Consistent Learning Network for CBCT Metal Artifact Reduction",
    "IEEE Transactions on Instrumentation and Measurement", "vol. 74, pp. 1-13, 2025",
    "10.1109/tim.2025.3551446", "journal", ["Yu"], "Medical imaging")
pub(2025, ["B. Morovati", "M. Li", "S. Han", "L. Zhou", "D. Wang", "G. Wang", "H. Yu"],
    "Patch-based dual-domain photon-counting CT data correction with residual-based WGAN-ViT",
    "Physics in Medicine & Biology", "vol. 70, no. 4, art. 045008, Feb. 2025",
    "10.1088/1361-6560/adaf71", "journal", ["Yu"], "Medical imaging")
pub(2025, ["B. Morovati", "S. Han", "L. Zhou", "D. Wang", "H. Yu"],
    "Photon-Counting CT Reconstruction Using Separable Attention-Based Tensor Neural Network Prior",
    "IEEE 22nd International Symposium on Biomedical Imaging (ISBI)", "pp. 1-4, Apr. 2025",
    "10.1109/isbi60581.2025.10981198", "conference", ["Yu"], "Medical imaging")
pub(2025, ["S. Han", "Y. Xu", "D. Wang", "B. Morovati", "L. Zhou", "J. S. Maltz", "G. Wang", "H. Yu"],
    "Physics-Informed Score-Based Diffusion Model for Limited-Angle Reconstruction of Cardiac Computed Tomography",
    "IEEE Transactions on Medical Imaging", "vol. 44, no. 9, pp. 3629-3640, Sept. 2025",
    "10.1109/tmi.2024.3494271", "journal", ["Yu"], "Medical imaging")
pub(2025, ["A. Kajenski", "G. Strack", "S. Khushrushahi", "A. Akyurtlu"],
    "Printed textile metasurfaces for gain and directivity enhancement",
    "Flexible and Printed Electronics", "vol. 10, no. 1, art. 015002, Jan. 2025",
    "10.1088/2058-8585/ada1e1", "journal", ["Akyurtlu"], "Printed electronics")
pub(2025, ["E. Lamport", "S. G. Avuthu", "S. Chen", "J. Mapkar", "A. Akyurtlu"],
    "Process Optimization of Additively Manufactured Conformal Temperature and Humidity Sensor for High-Temperature Applications",
    "Journal of Microelectronics and Electronic Packaging", "vol. 22, no. 1, Mar. 2025",
    "10.4071/001c.133286", "journal", ["Akyurtlu"], "Printed electronics")
pub(2025, ["F. Bottalico", "N. A. Valente", "C. Niezrecki", "K. Jerath", "Y. Luo", "A. Sabato"],
    "Rapid 3D Camera Calibration for Large-Scale Structural Monitoring",
    "Remote Sensing", "vol. 17, no. 15, art. 2720, Aug. 2025",
    "10.3390/rs17152720", "journal", ["Niezrecki", "Luo"], "Renewable energy and structural monitoring")
pub(2025, ["Y. Ding", "M. Z. Islama", "J. Shiau", "A. Amico", "Y. Tian", "Z. Jiang", "S. Ozharar", "T. Wang", "Y. Lin"],
    "Resilient DFOS placement strategy for power grid monitoring: integrating fiber and power network dependencies",
    "29th International Conference on Optical Fiber Sensors", "art. 70, May 2025",
    "10.1117/12.3060520", "conference", ["Lin"], "Smart grid")
pub(2025, ["H. Huang", "Y. Lin"],
    "Switching Dynamic State Estimation and Event Detection for Inverter-Based Resources With Multiple Control Modes",
    "IEEE Transactions on Power Systems", "vol. 40, no. 4, pp. 3439-3451, July 2025",
    "10.1109/tpwrs.2024.3523490", "journal", ["Lin"], "Smart grid")
pub(2025, ["Z. R. Khavas", "A. Majdi", "S. R. Azadeh", "P. Robinette"],
    "The Role of Drone Appearance and Capability in Human Trust: A Comparative vs. Isolated Analysis",
    "22nd International Conference on Ubiquitous Robots (UR)", "pp. 320-327, June 2025",
    "10.1109/ur65550.2025.11078060", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2025, ["P. Wu", "Y. Xu", "Z. Zhao", "Z. Liu", "X. Gao", "L. Ren", "Y. Zhang", "R. Guo", "H. Yu"],
    "Three dimensional segmentation of abdominal arteries and veins using vision transformers and domain adaptation",
    "Physics in Medicine & Biology", "vol. 71, no. 1, art. 015021, Dec. 2025",
    "10.1088/1361-6560/ae2c3b", "journal", ["Yu"], "Medical imaging")
pub(2025, ["Y. Chen", "Y. Xie", "C. Wang", "L. Yang", "N. Zheng", "L. Wu"],
    "Time-dependent effect of advanced driver assistance systems on driver behavior based on connected vehicle data",
    "Analytic Methods in Accident Research", "vol. 45, art. 100370, Mar. 2025",
    "10.1016/j.amar.2025.100370", "journal", ["Xie"], "Transportation")
pub(2025, ["Y. Chen", "Y. Xie", "S. Xu", "L. Zhao", "C. Wang"],
    "Trade-Offs Between Safety and Volatility in Driving Interactions: Evidence from A Connected Vehicle Pilot Study",
    "IEEE Intelligent Vehicles Symposium (IV)", "pp. 2089-2095, June 2025",
    "10.1109/iv64158.2025.11097600", "conference", ["Xie"], "Transportation")
pub(2025, ["Y. Chen", "C. Lu", "S. Xu", "M. Wu", "Y. Xie", "C. Wang"],
    "VUD-FC: A Heterogeneous Behavior-Oriented Adaptive Control Approach Using Variable Universe of Discourse Fuzzy Strategy",
    "IEEE 28th International Conference on Intelligent Transportation Systems (ITSC)", "pp. 2032-2038, Nov. 2025",
    "10.1109/itsc60802.2025.11423549", "conference", ["Xie"], "Transportation")
pub(2025, ["F. BOTTALICO", "J. S. SYED", "C. NIEZRECKI", "A. SABATO"],
    "mproving Image Resolution for Drone-Borne Inspection of Wind Turbine Blades",
    "Proceedings of the 15th International Workshop on Structural Health Monitoring", "Sept. 2025",
    "10.12783/shm2025/37411", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2025, ["L. Zhou", "C. Fang", "B. Morovati", "Y. Liu", "S. Han", "Y. Xu", "H. Yu"],
    "\u03c1-NeRF: Leveraging Attenuation Priors in Neural Radiance Field for 3d Computed Tomography Reconstruction",
    "IEEE International Conference on Image Processing (ICIP)", "pp. 1636-1641, Sept. 2025",
    "10.1109/icip55913.2025.11084616", "conference", ["Yu"], "Medical imaging")

# --- 2021-2024 papers of all center faculty (Crossref, vetted Sept. 2026)
pub(2024, ["J. Kasule", "S. Gnanou", "A. Akyurtlu", "C. Shemelya"],
    "A Multilayer Compact Circular Patch Antenna by Additive Manufacturing with Enhanced Bandwidth",
    "IEEE International Symposium on Antennas and Propagation and INC/USNC\u2010URSI Radio Science Meeting (AP-S/INC-USNC-URSI)", "pp. 2529-2530, July 2024",
    "10.1109/ap-s/inc-usnc-ursi52054.2024.10686023", "conference", ["Akyurtlu"], "Printed electronics")
pub(2024, ["H. Huang", "L. Ding", "Y. Lin", "X. Lu", "Y. Zheng"],
    "A Seamless Transition between Grid-Forming and Grid-Following Controls of Inverter-Based Resources",
    "IEEE Energy Conversion Congress and Exposition (ECCE)", "pp. 3692-3699, Oct. 2024",
    "10.1109/ecce55643.2024.10861248", "conference", ["Lin"], "Smart grid")
pub(2024, ["G. Cheng", "Y. Lin", "A. Abur", "A. G\u00f3mez-Exp\u00f3sito", "W. Wu"],
    "A Survey of Power System State Estimation Using Multiple Data Sources: PMUs, SCADA, AMI, and Beyond",
    "IEEE Transactions on Smart Grid", "vol. 15, no. 1, pp. 1129-1151, Jan. 2024",
    "10.1109/tsg.2023.3286401", "journal", ["Lin"], "Smart grid")
pub(2024, ["Y. Xu", "W. Ye", "Y. Xie", "C. Wang"],
    "A two-dimensional surrogate safety measure based on fuzzy logic model",
    "Accident Analysis & Prevention", "vol. 199, art. 107529, May 2024",
    "10.1016/j.aap.2024.107529", "journal", ["Xie"], "Transportation")
pub(2024, ["A. Baran", "J. Nelson-Slivon", "L. Tseng", "R. Palmieri"],
    "ALock: Asymmetric Lock Primitive for RDMA Systems",
    "Proceedings of the 36th ACM Symposium on Parallelism in Algorithms and Architectures", "pp. 15-26, June 2024",
    "10.1145/3626183.3659977", "conference", ["Tseng"], "Distributed systems")
pub(2024, ["Z. Xiong", "S. Chen", "Y. Zhang", "Y. Cao", "B. Liu", "X. Liu"],
    "Adaptify: A Refined Test-Time Adaptation Scheme for Frame Classification Consistency in Atrophic Gastritis Videos",
    "IEEE International Symposium on Biomedical Imaging (ISBI)", "pp. 1-5, May 2024",
    "10.1109/isbi56570.2024.10635341", "conference", ["Cao"], "Digital health")
pub(2024, ["J. Zhang", "H. Mao", "D. Chang", "H. Yu", "W. Wu", "D. Shen"],
    "Adaptive and Iterative Learning With Multi-Perspective Regularizations for Metal Artifact Reduction",
    "IEEE Transactions on Medical Imaging", "vol. 43, no. 9, pp. 3354-3365, Sept. 2024",
    "10.1109/tmi.2024.3395348", "journal", ["Yu"], "Medical imaging")
pub(2024, ["P. Wu", "Y. Qu", "Z. Zhao", "Y. Cui", "Y. Xu", "P. An", "H. Yu"],
    "An adaptive weighted ensemble learning network for diabetic retinopathy classification",
    "Journal of X-Ray Science and Technology: Clinical Applications of Diagnosis and Therapeutics", "vol. 32, no. 2, pp. 285-301, Jan. 2024",
    "10.3233/xst-230252", "journal", ["Yu"], "Medical imaging")
pub(2024, ["Z. Bhuyan", "L. Wu", "Y. Xie", "M. Shirazi", "Y. Cao", "B. Liu"],
    "Analyzing Highway Work Zone Traffic Dynamics via Drone Thermal Videos and Deep Learning",
    "IEEE 27th International Conference on Intelligent Transportation Systems (ITSC)", "pp. 792-797, Sept. 2024",
    "10.1109/itsc58415.2024.10919666", "conference", ["Xie", "Cao"], "Transportation")
pub(2024, ["R. Liu", "Y. Xie", "Z. Bhuyan"],
    "Assessing the Impacts of Merge and Speed Control Strategies on Highway Work Zone Safety and Operations Using Artificial Intelligence and Advanced Sensors",
    "IFAC-PapersOnLine", "vol. 58, no. 10, pp. 194-199, 2024",
    "10.1016/j.ifacol.2024.07.339", "journal", ["Xie"], "Transportation")
pub(2024, ["X. Liang", "Q. Chen", "Y. Cao", "B. Liu", "S. Chen", "X. Liu"],
    "Automated Scene Classification in Endoscopy Videos Using Convolutional Neural Networks",
    "IEEE/ACM Conference on Connected Health: Applications, Systems and Engineering Technologies (CHASE)", "pp. 157-161, June 2024",
    "10.1109/chase60773.2024.00026", "conference", ["Cao"], "Digital health")
pub(2024, ["A. A. Caiado", "S. Chaurasia", "S. R. Aravamuthan", "A. Roy", "M. Inalpolat", "E. Agar"],
    "Binder-Coated Carbon Cloth Electrodes for All-Vanadium Redox Flow Batteries",
    "Journal of The Electrochemical Society", "vol. 171, no. 12, art. 120524, Dec. 2024",
    "10.1149/1945-7111/ad9ad5", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2024, ["J. Zarnstorff", "L. Lebow", "D. Remuck", "C. Ruiz", "L. Tseng"],
    "Brief Announcement: Racos: A Leaderless Erasure Coding State Machine Replication",
    "Proceedings of the 36th ACM Symposium on Parallelism in Algorithms and Architectures", "pp. 379-381, June 2024",
    "10.1145/3626183.3660273", "conference", ["Tseng"], "Distributed systems")
pub(2024, ["A. Luce", "C. Areias", "S. Trulli", "E. Harper", "Y. Zhang", "G. Strack", "J. Lovaasen", "A. Akyurtlu"],
    "Conformally printed additively manufactured RF demonstrator for circuit compaction",
    "Flexible and Printed Electronics", "vol. 9, no. 4, art. 045007, Nov. 2024",
    "10.1088/2058-8585/ad8d64", "journal", ["Akyurtlu"], "Printed electronics")
pub(2024, ["K. Lowandy", "S. Kelliher", "D. Le", "C. Molinari", "I. Harris", "L. Unger", "R. Fink", "C. Shemelya", "P. Robinette"],
    "Convolutional neural networks for engineering design validation",
    "Applications of Machine Learning 2024", "art. 17, Oct. 2024",
    "10.1117/12.3027869", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["R. Dai", "Z. Liu", "O. Arias", "X. Guo", "T. Yavuz"],
    "DTjRTL: A Configurable Framework for Automated Hardware Trojan Insertion at RTL",
    "Proceedings of the Great Lakes Symposium on VLSI 2024", "pp. 465-470, June 2024",
    "10.1145/3649476.3658759", "conference", ["Arias"], "HPC and hardware")
pub(2024, ["H. K. Lee", "M. S. Kim", "M. Inalpolat", "E. Ozdemir"],
    "Development of In-wheel Motor System NVH Performance Analysis Tool and Its Application for In-wheel Motor NVH Development",
    "Transactions of the Korean Society for Noise and Vibration Engineering", "vol. 34, no. 2, pp. 180-187, Apr. 2024",
    "10.5050/ksnve.2024.34.2.180", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2024, ["Z. R. Khavas", "M. R. Kotturu", "R. Azadeh", "P. Robinette"],
    "Do Humans Have Different Expectations Regarding Humans and Robots\u2019 Morality?*",
    "33rd IEEE International Conference on Robot and Human Interactive Communication (ROMAN)", "pp. 1126-1133, Aug. 2024",
    "10.1109/ro-man60168.2024.10731315", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["Z. Rezaei Khavas", "M. R. Kotturu", "S. R. Ahmadzadeh", "P. Robinette"],
    "Do Humans Trust Robots that Violate Moral Trust?",
    "ACM Transactions on Human-Robot Interaction", "vol. 13, no. 2, pp. 1-30, June 2024",
    "10.1145/3651992", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["A. Rezaee", "R. McCann", "V. M. Vokkarane"],
    "Dynamic Crosstalk-Aware Routing, Modulation, Core, and Spectrum Allocation for Sliceable Demands in SDM-EONs",
    "IEEE 30th International Symposium on Local and Metropolitan Area Networks (LANMAN)", "pp. 76-81, July 2024",
    "10.1109/lanman61958.2024.10621885", "conference", ["Vokkarane"], "Optical networks")
pub(2024, ["H. Huang", "Y. Lin", "X. Lu", "Y. Zhao", "A. Kumar"],
    "Dynamic State Estimation for Inverter-Based Resources: A Control-Physics Dual Estimation Framework",
    "IEEE Transactions on Power Systems", "vol. 39, no. 5, pp. 6456-6468, Sept. 2024",
    "10.1109/tpwrs.2024.3362701", "journal", ["Lin"], "Smart grid")
pub(2024, ["J. Yoon", "A. Moon", "S. W. Son"],
    "Effective Posture Classification Using Statistically Significant Data From Flexible Pressure Sensors",
    "IEEE Journal on Flexible Electronics", "vol. 3, no. 5, pp. 173-180, May 2024",
    "10.1109/jflex.2024.3400151", "journal", ["Son"], "HPC and hardware")
pub(2024, ["G. Cheng", "Y. Lin"],
    "Enhanced Power System State Estimation With Overhead Line Sensors",
    "IEEE Transactions on Power Systems", "vol. 39, no. 5, pp. 6780-6783, Sept. 2024",
    "10.1109/tpwrs.2024.3405723", "journal", ["Lin"], "Smart grid")
pub(2024, ["R. McCann", "A. Rezaee", "V. M. Vokkarane"],
    "Enhancing Routing in SD-EONs through Reinforcement Learning: A Comparative Analysis",
    "IEEE Latin-American Conference on Communications (LATINCOM)", "pp. 1-6, Nov. 2024",
    "10.1109/latincom62985.2024.10770647", "conference", ["Vokkarane"], "Optical networks")
pub(2024, ["R. Liu", "Y. Xie", "P. Stamatiadis", "N. Gartner", "T. Ge"],
    "Enhancing Traffic Incident Detection Through ADASYN-Attention Fusion: A Comparative Study with RITIS Data",
    "IEEE 27th International Conference on Intelligent Transportation Systems (ITSC)", "pp. 1488-1493, Sept. 2024",
    "10.1109/itsc58415.2024.10919901", "conference", ["Xie"], "Transportation")
pub(2024, ["Z. Jia", "Z. Lin", "Y. Luo", "Z. A. Cardoso", "D. Wang", "G. H. Flock", "K. A. Thompson-Witrick", "H. Yu", "B. Zhang"],
    "Enhancing pathogen identification in cheese with high background microflora using an artificial neural network-enabled paper chromogenic array sensor approach",
    "Sensors and Actuators B: Chemical", "vol. 410, art. 135675, July 2024",
    "10.1016/j.snb.2024.135675", "journal", ["Yu"], "Medical imaging")
pub(2024, ["R. McCann", "A. Rezaee", "V. M. Vokkarane"],
    "FUSION: A Flexible Unified Simulator for Intelligent Optical Networking",
    "IEEE International Conference on Advanced Networks and Telecommunications Systems (ANTS)", "pp. 1-6, Dec. 2024",
    "10.1109/ants63515.2024.10898199", "conference", ["Vokkarane"], "Optical networks")
pub(2024, ["Q. Zhang", "L. Tseng"],
    "Fault-tolerant Consensus in Anonymous Dynamic Network",
    "IEEE 44th International Conference on Distributed Computing Systems (ICDCS)", "pp. 128-138, July 2024",
    "10.1109/icdcs60910.2024.00021", "conference", ["Tseng"], "Distributed systems")
pub(2024, ["Y. Gao", "K. Barhydt", "C. Niezrecki", "Y. Gu"],
    "Global-Position Tracking Control for Multi-Domain Bipedal Walking With Underactuation",
    "Journal of Dynamic Systems, Measurement, and Control", "vol. 147, no. 1, Aug. 2024",
    "10.1115/1.4065323", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2024, ["L. Zhou", "D. Wang", "Y. Xu", "S. Han", "B. Morovati", "S. Fan", "H. Yu"],
    "Gradient Guided Co-Retention Feature Pyramid Network for LDCT Image Denoising",
    "Lecture Notes in Computer Science", "pp. 153-163, 2024",
    "10.1007/978-3-031-72390-2_15", "chapter", ["Yu"], "Medical imaging")
pub(2024, ["X. Ma", "Y. Xie", "C. Chigan"],
    "Graph Convolutional Network Based Multi-Objective Meta-Deep Q-Learning for Eco-Routing",
    "IEEE Transactions on Intelligent Transportation Systems", "vol. 25, no. 7, pp. 7323-7338, July 2024",
    "10.1109/tits.2023.3348034", "journal", ["Xie", "Chigan"], "Transportation")
pub(2024, ["H. Yue", "W. Zhang", "U. C. Yilmaz", "T. Yildiz", "H. Huang", "H. Liu", "Y. Lin", "A. Abur"],
    "Graph-learning-assisted state estimation using sparse heterogeneous measurements",
    "Electric Power Systems Research", "vol. 235, art. 110644, Oct. 2024",
    "10.1016/j.epsr.2024.110644", "journal", ["Lin"], "Smart grid")
pub(2024, ["E. Meriaux", "Z. R. Khavas", "A. Majdi", "P. Robinette"],
    "How Does Trust in Simulations of Drone Failures Compare with Reality?",
    "10th International Conference on Automation, Robotics and Applications (ICARA)", "pp. 305-310, Feb. 2024",
    "10.1109/icara60736.2024.10553061", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["Z. R. Khavas", "P. Robinette"],
    "Human-Robot Interaction Experiment: Minor Changes; Significant Differences",
    "Proceedings of the Second International Symposium on Trustworthy Autonomous Systems", "pp. 1-13, Sept. 2024",
    "10.1145/3686038.3686056", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["Y. Xu", "S. Han", "D. Wang", "G. Wang", "J. S. Maltz", "H. Yu"],
    "Hybrid U-Net and Swin-transformer network for limited-angle cardiac computed tomography",
    "Physics in Medicine & Biology", "vol. 69, no. 10, art. 105012, Apr. 2024",
    "10.1088/1361-6560/ad3db9", "journal", ["Yu"], "Medical imaging")
pub(2024, ["S. H. Islam", "X. Ma", "C. Chigan"],
    "Hypernetwork-Based Adaptive Self-Interference Cancellation for Full-Duplex Wireless Communication Systems",
    "IEEE International Conference on Communications Workshops (ICC Workshops)", "pp. 644-649, June 2024",
    "10.1109/iccworkshops59551.2024.10615750", "conference", ["Chigan"], "Wireless networks")
pub(2024, ["Y. Zhang", "Y. Zou", "Y. Xie", "L. Chen"],
    "Identifying dynamic interaction patterns in mandatory and discretionary lane changes using graph structure",
    "Computer-Aided Civil and Infrastructure Engineering", "vol. 39, no. 5, pp. 638-655, Mar. 2024",
    "10.1111/mice.13099", "journal", ["Xie"], "Transportation")
pub(2024, ["B. Sarikaya", "M. Inalpolat"],
    "Impact of Periodic Path Imperfections on Dynamic Response of Centrifugal Pendulum Vibration Absorbers",
    "Conference Proceedings of the Society for Experimental Mechanics Series", "pp. 81-89, 2024",
    "10.1007/978-3-031-68901-7_11", "chapter", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2024, ["E. T. Ozdemir", "M. Inalpolat"],
    "Impact of Ring Gear Dynamics on Planet Load Sharing",
    "Volume 10: 2024 International Power Transmission and Gearing Conference (PTG)", "Aug. 2024",
    "10.1115/detc2024-142539", "conference", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2024, ["B. Morovati", "M. Li", "S. Han", "Y. Xu", "L. Zhou", "G. Wang", "H. Yu"],
    "Impact of network architecture and training strategy for photon counting CT data correction",
    "Developments in X-Ray Tomography XV", "art. 65, Oct. 2024",
    "10.1117/12.3027262", "conference", ["Yu"], "Medical imaging")
pub(2024, ["N. N. Kulkarni", "L. Peretto", "F. Bottalico", "C. Niezrecki", "A. Sabato"],
    "Infrared-based point cloud reconstruction for heat loss detection in a virtual reality environment",
    "NDE 4.0, Predictive Maintenance, Communication, and Energy Systems: The Digital Transformation of NDE II", "art. 7, May 2024",
    "10.1117/12.3009908", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2024, ["M. S. Tanveer", "C. Wiedeman", "Y. Shi", "H. Yu", "G. Wang"],
    "Interior photon-counting CT data denoising via multi-agent reinforcement learning",
    "Developments in X-Ray Tomography XV", "art. 10, Oct. 2024",
    "10.1117/12.3029551", "conference", ["Yu"], "Medical imaging")
pub(2024, ["C. A. Ng", "C. Pozzi", "S. Lyon", "M. Inalpolat", "C. Niezrecki", "Y. Luo"],
    "IoT acoustic sensor design and antenna selection for a wind turbine structural health monitoring system",
    "NDE 4.0, Predictive Maintenance, Communication, and Energy Systems: The Digital Transformation of NDE II", "art. 10, May 2024",
    "10.1117/12.3010478", "conference", ["Inalpolat", "Niezrecki"], "Structural dynamics and health monitoring")
pub(2024, ["J. Pan", "H. Yu", "Z. Gao", "S. Wang", "H. Zhang", "W. Wu"],
    "Iterative Residual Optimization Network for Limited-Angle Tomographic Reconstruction",
    "IEEE Transactions on Image Processing", "vol. 33, pp. 910-925, 2024",
    "10.1109/tip.2024.3351382", "journal", ["Yu"], "Medical imaging")
pub(2024, ["L. Tseng", "G. Liang", "N. H. Vaidya"],
    "Iterative approximate Byzantine consensus in arbitrary directed graphs",
    "Distributed Computing", "vol. 37, no. 3, pp. 225-246, May 2024",
    "10.1007/s00446-024-00468-2", "journal", ["Tseng"], "Distributed systems")
pub(2024, ["M. Z. Islam", "W. Zhang", "Y. Lin"],
    "Learning-Based Customer Voltage Visibility With Sparse High-Reporting-Rate Smart Meters",
    "IEEE Power & Energy Society General Meeting (PESGM)", "pp. 1-5, July 2024",
    "10.1109/pesgm51994.2024.10688681", "conference", ["Lin"], "Smart grid")
pub(2024, ["D. Wang", "S. Han", "Y. Xu", "Z. Wu", "L. Zhou", "B. Morovati", "H. Yu"],
    "LoMAE: Simple Streamlined Low-Level Masked Autoencoders for Robust, Generalized, and Interpretable Low-Dose CT Denoising",
    "IEEE Journal of Biomedical and Health Informatics", "vol. 28, no. 11, pp. 6815-6827, Nov. 2024",
    "10.1109/jbhi.2024.3454979", "journal", ["Yu"], "Medical imaging")
pub(2024, ["T. L. Huoh", "T. Miskell", "O. Barut", "Y. Luo", "P. Li", "T. Zhang"],
    "Malware Detection for Portable Executables Using a Multi-input Transformer-Based Approach",
    "International Conference on Computing, Networking and Communications (ICNC)", "pp. 778-782, Feb. 2024",
    "10.1109/icnc59896.2024.10556067", "conference", ["Luo"], "Sensing and networks")
pub(2024, ["Z. Liu", "K. Chen", "D. Sullivan", "O. Arias", "R. Dutta", "Y. Jin", "X. Guo"],
    "Microscope: Causality Inference Crossing the Hardware and Software Boundary from Hardware Perspective",
    "29th Asia and South Pacific Design Automation Conference (ASP-DAC)", "pp. 933-938, Jan. 2024",
    "10.1109/asp-dac58780.2024.10473793", "conference", ["Arias"], "HPC and hardware")
pub(2024, ["Y. Chen", "C. Wang", "Y. Xie"],
    "Modeling the risk of single-vehicle run-off-road crashes on horizontal curves using connected vehicle data",
    "Analytic Methods in Accident Research", "vol. 43, art. 100333, Sept. 2024",
    "10.1016/j.amar.2024.100333", "journal", ["Xie"], "Transportation")
pub(2024, ["L. Tseng", "L. Ambarapu", "M. Aloqaily"],
    "NC-DHT: a Robust and Anonymous DHT for Blockchain Systems",
    "6th International Conference on Blockchain Computing and Applications (BCCA)", "pp. 394-399, Nov. 2024",
    "10.1109/bcca62388.2024.10844445", "conference", ["Tseng"], "Distributed systems")
pub(2024, ["A. Berkowitz", "A. A. Caiado", "S. R. Aravamuthan", "A. Roy", "E. Agar", "M. Inalpolat"],
    "Optimization framework for redox flow battery electrodes with improved microstructural characteristics",
    "Energy Advances", "vol. 3, no. 9, pp. 2220-2237, 2024",
    "10.1039/d4ya00248b", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2024, ["G. Cheng", "Y. Lin"],
    "Power System Adaptive State Estimation in Unknown Measurement Environment",
    "IEEE Transactions on Instrumentation and Measurement", "vol. 73, pp. 1-17, 2024",
    "10.1109/tim.2024.3403203", "journal", ["Lin"], "Smart grid")
pub(2024, ["J. Zarnstorff", "L. Lebow", "C. Siems", "D. Remuck", "C. Ruiz", "L. Tseng"],
    "Racos: Improving Erasure Coding State Machine Replication using Leaderless Consensus",
    "Proceedings of the ACM Symposium on Cloud Computing", "pp. 600-617, Nov. 2024",
    "10.1145/3698038.3698511", "conference", ["Tseng"], "Distributed systems")
pub(2024, ["S. N. Edib", "V. M. Vokkarane", "Y. Lin"],
    "Reinforcement Learning-Based Observability-Aware Cyber Restoration of Power Grid",
    "IEEE Global Communications Conference", "pp. 1599-1604, Dec. 2024",
    "10.1109/globecom52923.2024.10901146", "conference", ["Vokkarane", "Lin"], "Optical networks")
pub(2024, ["Y. Findik", "P. Robinette", "K. Jerath", "R. Azadeh"],
    "Relational Q-Functionals: Multi-Agent Learning to Recover from Unforeseen Robot Malfunctions in Continuous Action Domains",
    "21st International Conference on Ubiquitous Robots (UR)", "pp. 251-256, June 2024",
    "10.1109/ur61395.2024.10597441", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["M. R. Kotturu", "S. V. Movahed", "P. Robinette", "K. Jerath", "A. Redlich", "R. Azadeh"],
    "Relational Weight Optimization for Enhancing Team Performance in Multi-Agent Multi-Armed Bandits",
    "IFAC-PapersOnLine", "vol. 58, no. 28, pp. 492-497, 2024",
    "10.1016/j.ifacol.2025.01.094", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2024, ["M. Benker", "G. Gu", "A. Senckowski", "B. Xiang", "C. Dwyer", "R. Adams", "Y. Xie", "R. Nagarajan", "Y. Li", "X. Lu"],
    "Room-Temperature (RT) Extended Short-Wave Infrared (e-SWIR) Avalanche Photodiode (APD) with a 2.6 \u00b5m Cutoff Wavelength",
    "Micromachines", "vol. 15, no. 8, art. 941, July 2024",
    "10.3390/mi15080941", "journal", ["Xie"], "Transportation")
pub(2024, ["Y. Liang", "M. Li", "S. Han", "H. Yu", "G. Wang"],
    "SPECT with a Compton camera for thyroid cancer imaging",
    "Developments in X-Ray Tomography XV", "art. 75, Oct. 2024",
    "10.1117/12.3028247", "conference", ["Yu"], "Medical imaging")
pub(2024, ["Y. Dai", "C. Wang", "Y. Xie"],
    "Safety-oriented automated vehicle longitudinal control considering both stability and damping behavior",
    "Accident Analysis & Prevention", "vol. 198, art. 107486, Apr. 2024",
    "10.1016/j.aap.2024.107486", "journal", ["Xie"], "Transportation")
pub(2024, ["S. N. Edib", "Y. Lin", "V. M. Vokkarane", "F. Qiu", "Y. Zhang", "P. Du"],
    "Situation-Aware Load Restoration Considering Uncertainty and Correlation",
    "IEEE Transactions on Power Systems", "vol. 39, no. 2, pp. 2611-2629, Mar. 2024",
    "10.1109/tpwrs.2023.3278266", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2024, ["L. Ding", "Y. Men", "H. Huang", "X. Lu", "J. Qin", "Y. Lin", "J. Tan"],
    "Small-Signal Stability Constrained Optimal Power Flow of Inverter-Dominated Power Systems with Flexible Operation Mode Selection",
    "IEEE Energy Conversion Congress and Exposition (ECCE)", "pp. 4068-4073, Oct. 2024",
    "10.1109/ecce55643.2024.10861549", "conference", ["Lin"], "Smart grid")
pub(2024, ["F. Castro", "K. Chandra", "O. Arias"],
    "SoK: Sensor wars: Attacks and defenses on acoustic sensors",
    "The Journal of the Acoustical Society of America", "vol. 155, no. 3_Supplement, pp. A69-A69, Mar. 2024",
    "10.1121/10.0026830", "journal", ["Arias"], "HPC and hardware")
pub(2024, ["H. Shao", "C. Xu", "S. Haque", "Y. Xie"],
    "Special issue on technology in safety",
    "Accident Analysis & Prevention", "vol. 195, art. 107153, Feb. 2024",
    "10.1016/j.aap.2023.107153", "journal", ["Xie"], "Transportation")
pub(2024, ["Z. Li", "K. An", "H. Yu", "F. Luo", "J. Pan", "S. Wang", "J. Zhang", "W. Wu", "D. Chang"],
    "Spectrum learning for super-resolution tomographic reconstruction",
    "Physics in Medicine & Biology", "vol. 69, no. 8, art. 085018, Apr. 2024",
    "10.1088/1361-6560/ad2a94", "journal", ["Yu"], "Medical imaging")
pub(2024, ["Y. Chen", "Y. Xie", "C. Wang", "S. Xu", "L. Wu"],
    "Temporal Dependency of Forward Collision Warning Effectiveness: A Functional Framework for Speed Profiles After Receiving Warnings",
    "IEEE 27th International Conference on Intelligent Transportation Systems (ITSC)", "pp. 1793-1798, Sept. 2024",
    "10.1109/itsc58415.2024.10919910", "conference", ["Xie"], "Transportation")
pub(2024, ["Z. Bhuyan", "Y. Xie", "R. Liu", "Y. Cao", "B. Liu"],
    "Towards Safer Highway Work Zones: Insights from Deep Learning Analysis of Thermal Footage",
    "IFAC-PapersOnLine", "vol. 58, no. 10, pp. 188-193, 2024",
    "10.1016/j.ifacol.2024.07.338", "journal", ["Xie"], "Transportation")
pub(2024, ["H. Yue", "M. M. Ali", "Y. Lin", "H. Liu"],
    "Ultra-Short-Term Forecasting of Large Distributed Solar PV Fleets Using Sparse Smart Inverter Data",
    "IEEE Transactions on Sustainable Energy", "vol. 15, no. 3, pp. 1968-1980, July 2024",
    "10.1109/tste.2024.3390578", "journal", ["Lin"], "Smart grid")
pub(2024, ["E. Vergara", "J. Aviles-Ordonez", "Y. Xie", "M. Shirazi"],
    "Understanding speeding behavior on interstate horizontal curves and ramps using networkwide probe data",
    "Journal of Safety Research", "vol. 90, pp. 371-380, Sept. 2024",
    "10.1016/j.jsr.2024.05.003", "journal", ["Xie"], "Transportation")
pub(2023, ["X. Wang", "Z. Zhang", "Q. Chen", "Y. Yin", "G. Lian", "S. Chen", "X. Liu", "Y. Cao", "B. Liu"],
    "A CNN-Based Disease Detection Framework for Wireless Capsule Endoscopy Videos",
    "IEEE International Conference on E-health Networking, Application &amp; Services (Healthcom)", "pp. 164-170, Dec. 2023",
    "10.1109/healthcom56612.2023.10472369", "conference", ["Cao"], "Digital health")
pub(2023, ["A. L. Kajenski", "S. Khushrushahi", "G. Strack", "A. Akyurtlu"],
    "A Comparison of Wearable Metasurfaces",
    "IEEE 73rd Electronic Components and Technology Conference (ECTC)", "pp. 2235-2239, May 2023",
    "10.1109/ectc51909.2023.00387", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["O. Barut", "T. Zhang", "Y. Luo", "P. Li"],
    "A Comprehensive Study on Efficient and Accurate Machine Learning-Based Malicious PE Detection",
    "IEEE 20th Consumer Communications & Networking Conference (CCNC)", "pp. 632-635, Jan. 2023",
    "10.1109/ccnc51644.2023.10060214", "conference", ["Luo"], "Sensing and networks")
pub(2023, ["S. N. Edib", "Y. Lin", "V. M. Vokkarane", "X. Fan"],
    "A Cross-Domain Optimization Framework of PMU and Communication Placement for Multidomain Resiliency and Cost Reduction",
    "IEEE Internet of Things Journal", "vol. 10, no. 9, pp. 7490-7504, May 2023",
    "10.1109/jiot.2022.3184946", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["X. Wang", "Z. Zhang", "J. Guo", "P. Zhang", "Q. Chen", "Y. Cao", "X. Fu", "B. Liu"],
    "A Greedy Algorithm-Based Self-Training Pipeline for Expansion of Dental Caries Dataset",
    "IEEE International Conference on E-health Networking, Application &amp; Services (Healthcom)", "pp. 26-32, Dec. 2023",
    "10.1109/healthcom56612.2023.10472373", "conference", ["Cao"], "Digital health")
pub(2023, ["M. Z. Islam", "S. N. Edib", "V. M. Vokkarane", "Y. Lin", "X. Fan"],
    "A Scalable PDC Placement Technique for Fast and Resilient Monitoring of Large Power Grids",
    "IEEE Transactions on Control of Network Systems", "vol. 10, no. 4, pp. 1770-1782, Dec. 2023",
    "10.1109/tcns.2023.3240200", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["C. Areias", "Y. Piro", "O. Ranasingha", "A. Akyurtlu"],
    "A new technique for 3D printing dielectric structures using aerosol-jettable photopolymers",
    "Flexible and Printed Electronics", "vol. 8, no. 1, art. 015009, Feb. 2023",
    "10.1088/2058-8585/acb3dd", "journal", ["Akyurtlu", "Ranasingha"], "Printed electronics")
pub(2023, ["L. Jiang", "Y. Xie", "N. G. Evans"],
    "A simulation study of cooperative and autonomous vehicles (CAV) considering courtesy, ethics, and fairness",
    "PLOS ONE", "vol. 18, no. 5, art. e0283649, May 2023",
    "10.1371/journal.pone.0283649", "journal", ["Xie"], "Transportation")
pub(2023, ["C. Areias", "A. Luce", "Y. Piro", "A. Akyurtlu"],
    "Additive Integration with Aerosol-Jet Printed SIWs",
    "53rd European Microwave Conference (EuMC)", "pp. 227-230, Sept. 2023",
    "10.23919/eumc58039.2023.10290163", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["C. Areias", "E. Lamport", "Y. Piro", "M. Cason", "C. Armiento", "A. Akyurtlu"],
    "Additive Packaging for Bare Die and Additively Integrated Antenna",
    "IMAPSource Proceedings", "vol. 2022, no. IMAPS Symposium, May 2023",
    "10.4071/001c.74545", "journal", ["Akyurtlu"], "Printed electronics")
pub(2023, ["E. Lamport", "A. Luce", "Y. Piro", "S. Trulli", "A. Akyurtlu"],
    "Additively Manufactured Near Chip Scale Interposers for DC and RF Applications",
    "IEEE 73rd Electronic Components and Technology Conference (ECTC)", "pp. 2207-2212, May 2023",
    "10.1109/ectc51909.2023.00382", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["C. Traylor", "M. Inalpolat", "D. J. Willis", "P. O. Persson"],
    "Aeroacoustics-Based Structural Health Monitoring of Airfoils with Surface Damage and Domain Coupling",
    "AIAA Journal", "vol. 61, no. 11, pp. 5187-5190, Nov. 2023",
    "10.2514/1.j062814", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2023, ["J. Boffie", "S. Aghara", "K. Bogannam", "V. F. Almeida"],
    "An Efficient Fractional Neutron Point Kinetics Approach to Simulating Reactor Transients",
    "Transactions of the American Nuclear Society", "vol. 128, pp. 787-790, 2023",
    "10.13182/t130-42226", "conference", ["Aghara"], "Nuclear energy and security")
pub(2023, ["A. Moon", "M. Kim", "J. Chen", "S. W. Son"],
    "Anomaly Detection in Scientific Datasets using Sparse Representation",
    "Proceedings of the First Workshop on AI for Systems", "pp. 13-18, Aug. 2023",
    "10.1145/3588982.3603610", "conference", ["Son"], "HPC and hardware")
pub(2023, ["G. Strack", "J. H. Kim", "S. Giardini", "A. Akyurtlu", "R. M. Osgood"],
    "Application of a magnetic field to ferromagnetic diodes",
    "MRS Advances", "vol. 8, no. 5, pp. 188-193, Feb. 2023",
    "10.1557/s43580-023-00520-6", "journal", ["Akyurtlu"], "Printed electronics")
pub(2023, ["S. U. Dabetwar", "C. Niezrecki", "A. Sabato"],
    "Application of mask RCNN for localizing and quantifying areas of energy leak in buildings using infrared images",
    "Health Monitoring of Structural and Biological Systems XVII", "art. 44, Apr. 2023",
    "10.1117/12.2655785", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["L. Han", "F. Li", "H. Yu", "K. Xia", "Q. Xin", "X. Zou"],
    "BiRPN-YOLOvX: A weighted bidirectional recursive feature pyramid algorithm for lung nodule detection",
    "Journal of X-Ray Science and Technology", "vol. 31, no. 2, pp. 301-317, Jan. 2023",
    "10.3233/xst-221310", "journal", ["Yu"], "Medical imaging")
pub(2023, ["D. Wang", "F. Fan", "Z. Wu", "R. Liu", "F. Wang", "H. Yu"],
    "CTformer: convolution-free Token2Token dilated vision transformer for low-dose CT denoising",
    "Physics in Medicine & Biology", "vol. 68, no. 6, art. 065012, Mar. 2023",
    "10.1088/1361-6560/acc000", "journal", ["Yu"], "Medical imaging")
pub(2023, ["B. Hammerstrom", "C. Niezrecki", "K. Hellman", "X. Jin", "M. B. Ross", "J. H. Mack", "E. Agar", "J. P. Trelles", "F. Liu", "F. Che", "D. Ryan", "M. S. Narasimhadevara", "M. Usovicz"],
    "Corrigendum: The viability of implementing hydrogen in the commonwealth of Massachusetts",
    "Frontiers in Energy Research", "vol. 11, May 2023",
    "10.3389/fenrg.2023.1179305", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["L. Tseng", "M. Aloqaily"],
    "Cryptocurrency meets CAP Theorem",
    "IEEE International Conference on Blockchain and Cryptocurrency (ICBC)", "pp. 1-2, May 2023",
    "10.1109/icbc56567.2023.10174927", "conference", ["Tseng"], "Distributed systems")
pub(2023, ["S. N. Edib", "Y. Lin", "V. M. Vokkarane", "F. Qiu", "R. Yao", "B. Chen"],
    "Cyber Restoration of Power Systems: Concept and Methodology for Resilient Observability",
    "IEEE Transactions on Systems, Man, and Cybernetics: Systems", "vol. 53, no. 8, pp. 5185-5198, Aug. 2023",
    "10.1109/tsmc.2023.3258412", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["S. K. Aghara", "C. Spirito"],
    "Cyber Security for Nuclear Facilities",
    "The Oxford Handbook of Nuclear Security", "pp. 309-324, Aug. 2023",
    "10.1093/oxfordhb/9780192847935.013.29", "chapter", ["Aghara"], "Nuclear energy and security")
pub(2023, ["M. Z. Islam", "Y. Lin", "V. M. Vokkarane", "Y. Yao", "F. Ding"],
    "Cyber-Physical Reconfiguration for Disaster Resilience of Power Distribution Systems",
    "IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)", "pp. 1-6, Oct. 2023",
    "10.1109/smartgridcomm57358.2023.10333954", "conference", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["M. Z. Islam", "Y. Lin", "V. M. Vokkarane", "V. Venkataramanan"],
    "Cyber-physical cascading failure and resilience of power grid: A comprehensive review",
    "Frontiers in Energy Research", "vol. 11, Feb. 2023",
    "10.3389/fenrg.2023.1095303", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["H. Huang", "Y. Lin", "Y. Zhou", "Y. Zhao", "P. Zhang", "L. Fan"],
    "Data-driven modeling of power system dynamics: Challenges, state of the art, and future work",
    "iEnergy", "vol. 2, no. 3, pp. 200-221, Sept. 2023",
    "10.23919/ien.2023.0023", "journal", ["Lin"], "Smart grid")
pub(2023, ["Z. Wu", "X. Zhong", "T. Lyv", "D. Wang", "R. Chen", "X. Yan", "G. Coatrieux", "X. Ji", "H. Yu", "Y. Chen", "X. Mai"],
    "Deep Dual-Domain United Guiding Learning With Global\u2013Local Transformer-Convolution U-Net for LDCT Reconstruction",
    "IEEE Transactions on Instrumentation and Measurement", "vol. 72, pp. 1-15, 2023",
    "10.1109/tim.2023.3329200", "journal", ["Yu"], "Medical imaging")
pub(2023, ["X. Ma", "M. Shahbakhti", "C. Chigan"],
    "Deep Learning Based Distributed Meta-Learning for Fast and Accurate Online Adaptive Powertrain Fuel Consumption Modeling",
    "IEEE Transactions on Vehicular Technology", "vol. 72, no. 6, pp. 7251-7264, June 2023",
    "10.1109/tvt.2023.3239943", "journal", ["Chigan"], "Wireless networks")
pub(2023, ["J. Parsons", "J. Winslow", "L. Tseng"],
    "Demo: Velox: Enhancing P2P Real-Time Communication in Browsers",
    "IEEE International Conference on Pervasive Computing and Communications Workshops and other Affiliated Events (PerCom Workshops)", "pp. 291-293, Mar. 2023",
    "10.1109/percomworkshops56833.2023.10150343", "conference", ["Tseng"], "Distributed systems")
pub(2023, ["Y. Chu", "F. Chen", "H. Fu", "H. Yu"],
    "Detection of Air Pollution in Urban Areas Using Monitoring Images",
    "Atmosphere", "vol. 14, no. 5, art. 772, Apr. 2023",
    "10.3390/atmos14050772", "journal", ["Yu"], "Medical imaging")
pub(2023, ["Y. Piro", "C. Aerias", "A. Luce", "E. Lamport", "Y. Li", "S. Trulli", "A. Akyurtlu"],
    "Development of a Photopolymer-Based Dielectric Nanocomposite for High Resolution Direct-Write Processes",
    "IMAPSource Proceedings", "vol. 2022, no. IMAPS Symposium, May 2023",
    "10.4071/001c.74629", "journal", ["Akyurtlu"], "Printed electronics")
pub(2023, ["A. Kajenski", "G. Strack", "S. Khushrushahi", "A. Akyurtlu"],
    "Direct-Write Printed Wearable Metasurfaces",
    "IMAPSource Proceedings", "vol. 2022, no. IMAPS Symposium, May 2023",
    "10.4071/001c.74553", "journal", ["Akyurtlu"], "Printed electronics")
pub(2023, ["S. N. Edib", "Y. Lin", "V. Vokkarane"],
    "Disaster-Resilient PMU Network Design",
    "ICC 2023 - IEEE International Conference on Communications", "pp. 4106-4112, May 2023",
    "10.1109/icc45041.2023.10279292", "conference", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["L. Tseng", "N. Zhou", "C. Dumas", "T. Bantikyan", "R. Palmieri"],
    "Distributed Multi-writer Multi-reader Atomic Register with Optimistically Fast Read and Write",
    "Proceedings of the 35th ACM Symposium on Parallelism in Algorithms and Architectures", "pp. 479-488, June 2023",
    "10.1145/3558481.3591086", "conference", ["Tseng"], "Distributed systems")
pub(2023, ["N. A. Valente", "C. T. do Cabo", "Z. Mao", "C. Niezrecki"],
    "Dynamic Mode Decomposition for Resonant Frequency Identification of Oscillating Structures",
    "Conference Proceedings of the Society for Experimental Mechanics Series", "pp. 155-162, Nov. 2023",
    "10.1007/978-3-031-34910-2_19", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["A. Kumar", "Y. Lin", "H. Huang", "X. Lu", "Y. Zhao"],
    "Dynamic-State-Estimation-Based Cyber Attack Detection for Inverter-Based Resources",
    "IEEE Power & Energy Society General Meeting (PESGM)", "pp. 1-5, July 2023",
    "10.1109/pesgm52003.2023.10252357", "conference", ["Lin"], "Smart grid")
pub(2023, ["L. Jiang", "Y. Xie", "N. G. Evans", "D. Chen"],
    "Empirical study of a cooperative longitudinal control for merging maneuvers considering courtesy and mixed autonomy",
    "Journal of Intelligent Transportation Systems", "vol. 28, no. 4, pp. 573-586, Feb. 2023",
    "10.1080/15472450.2023.2174802", "journal", ["Xie"], "Transportation")
pub(2023, ["J. Cimorelli", "B. Hammerstrom", "C. Niezrecki", "X. Jin"],
    "Estimate of the wind energy needed to replace natural gas with hydrogen, and electrify heat pumps and automobiles in Massachusetts",
    "Wind Engineering", "vol. 47, no. 6, pp. 1182-1200, July 2023",
    "10.1177/0309524x231185322", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["A. J. London", "Y. S. Razin", "J. Borenstein", "M. Eslami", "R. Perkins", "P. Robinette"],
    "Ethical Issues in Near-Future Socially Supportive Smart Assistants for Older Adults",
    "IEEE Transactions on Technology and Society", "vol. 4, no. 4, pp. 291-301, Dec. 2023",
    "10.1109/tts.2023.3237124", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2023, ["F. Bottalico", "C. Niezrecki", "K. Jerath", "Y. Luo", "A. Sabato"],
    "Experimental Quantification of Sensor-Based Stereocameras\u2019 Extrinsic Parameters Calibration",
    "Conference Proceedings of the Society for Experimental Mechanics Series", "pp. 49-55, Nov. 2023",
    "10.1007/978-3-031-34910-2_6", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["Y. Dai", "C. Wang", "Y. Xie"],
    "Explicitly incorporating surrogate safety measures into connected and automated vehicle longitudinal control objectives for enhancing platoon safety",
    "Accident Analysis & Prevention", "vol. 183, art. 106975, Apr. 2023",
    "10.1016/j.aap.2023.106975", "journal", ["Xie"], "Transportation")
pub(2023, ["A. Moon", "S. W. Son", "M. Kim", "S. Chang", "H. Park"],
    "Exploration Of Lossy Posture Classification Model Using In-Bed Flexible Pressure Sensors",
    "IEEE International Conference on Flexible and Printable Sensors and Systems (FLEPS)", "pp. 1-4, July 2023",
    "10.1109/fleps57599.2023.10220219", "conference", ["Son"], "HPC and hardware")
pub(2023, ["G. Strack", "A. Akyurtlu"],
    "Exploration of diode behavior in an applied magnetic field",
    "Nanoengineering: Fabrication, Properties, Optics, Thin Films, and Devices XX", "art. 26, Oct. 2023",
    "10.1117/12.2677864", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["A. A. Caiado", "S. Chaurasia", "S. R. Aravamuthan", "B. R. Howell", "M. Inalpolat", "J. W. Gallaway", "E. Agar"],
    "Exploring the Effectiveness of Carbon Cloth Electrodes for All-Vanadium Redox Flow Batteries",
    "Journal of The Electrochemical Society", "vol. 170, no. 11, art. 110525, Nov. 2023",
    "10.1149/1945-7111/ad0a80", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2023, ["T. L. Huoh", "Y. Luo", "P. Li", "T. Zhang"],
    "Flow-Based Encrypted Network Traffic Classification With Graph Neural Networks",
    "IEEE Transactions on Network and Service Management", "vol. 20, no. 2, pp. 1224-1237, June 2023",
    "10.1109/tnsm.2022.3227500", "journal", ["Luo"], "Sensing and networks")
pub(2023, ["J. Yuan", "F. Zhou", "Z. Guo", "X. Li", "H. Yu"],
    "HCformer: Hybrid CNN-Transformer for LDCT Image Denoising",
    "Journal of Digital Imaging", "vol. 36, no. 5, pp. 2290-2305, June 2023",
    "10.1007/s10278-023-00842-9", "journal", ["Yu"], "Medical imaging")
pub(2023, ["A. R. Mavurapu", "H. Shan", "X. Guo", "O. Arias", "D. Sullivan"],
    "HeisenTrojans: They Are Not There Until They Are Triggered",
    "Asian Hardware Oriented Security and Trust Symposium (AsianHOST)", "pp. 1-7, Dec. 2023",
    "10.1109/asianhost59942.2023.10409305", "conference", ["Arias"], "HPC and hardware")
pub(2023, ["J. Kasule", "A. Akyurtlu", "C. Armiento"],
    "High Speed Digital Signaling in Printed, Planar Microwave Connectors with Multiple Signal Lines",
    "IEEE 32nd Conference on Electrical Performance of Electronic Packaging and Systems (EPEPS)", "pp. 1-3, Oct. 2023",
    "10.1109/epeps58208.2023.10314934", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["N. A. Valente", "Z. Mao", "C. Niezrecki"],
    "Holistically Nested Edge Detection and particle filtering for subtle vibration extraction",
    "Mechanical Systems and Signal Processing", "vol. 204, art. 110753, Dec. 2023",
    "10.1016/j.ymssp.2023.110753", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["Z. R. Khavas", "A. Majdi", "S. R. Ahmadzadeh", "P. Robinette"],
    "Human Trust After Drone Failure: Study of the Effects of Drone Type and Failure Type on Human-Drone Trust",
    "20th International Conference on Ubiquitous Robots (UR)", "pp. 685-692, June 2023",
    "10.1109/ur57808.2023.10202489", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2023, ["S. Wang", "A. Cai", "W. Wu", "T. Zhang", "F. Liu", "H. Yu"],
    "IMD-MTFC: Image-Domain Material Decomposition via Material-Image Tensor Factorization and Clustering for Spectral CT",
    "IEEE Transactions on Radiation and Plasma Medical Sciences", "vol. 7, no. 4, pp. 382-393, Apr. 2023",
    "10.1109/trpms.2023.3234613", "journal", ["Yu"], "Medical imaging")
pub(2023, ["K. Chen", "O. Arias", "X. Guo", "Q. Deng", "Y. Jin"],
    "IP-Tag: Tag-Based Runtime 3PIP Hardware Trojan Detection in SoC Platforms",
    "IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems", "vol. 42, no. 1, pp. 68-81, Jan. 2023",
    "10.1109/tcad.2022.3174171", "journal", ["Arias"], "HPC and hardware")
pub(2023, ["A. Kumar", "Y. Lin", "X. Lu"],
    "Identification of Power Islands via Event-Triggered Decaying Current Injection by Inverter Networks",
    "IEEE Power & Energy Society General Meeting (PESGM)", "pp. 1-5, July 2023",
    "10.1109/pesgm52003.2023.10253294", "conference", ["Lin"], "Smart grid")
pub(2023, ["S. Wang", "W. Wu", "A. Cai", "Y. Xu", "V. Vardhanabhuti", "F. Liu", "H. Yu"],
    "Image-spectral decomposition extended-learning assisted by sparsity for multi-energy computed tomography reconstruction",
    "Quantitative Imaging in Medicine and Surgery", "vol. 13, no. 2, pp. 610-630, Feb. 2023",
    "10.21037/qims-22-235", "journal", ["Yu"], "Medical imaging")
pub(2023, ["Y. Findik", "P. Robinette", "K. Jerath", "S. R. Ahmadzadeh"],
    "Impact of Relational Networks in Multi-Agent Learning: A Value-Based Factorization View",
    "62nd IEEE Conference on Decision and Control (CDC)", "pp. 4447-4454, Dec. 2023",
    "10.1109/cdc49753.2023.10383543", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2023, ["J. Noel", "D. Lee", "J. Correia", "S. Aghara", "G. Fakhri"],
    "In Target Pressure Evaluation for Production of Zirconium-89",
    "Transactions of the American Nuclear Society", "vol. 128, pp. 198-200, 2023",
    "10.13182/t130-42144", "conference", ["Aghara"], "Nuclear energy and security")
pub(2023, ["Y. Findik", "H. Osooli", "P. Robinette", "K. Jerath", "S. R. Ahmadzadeh"],
    "Influence of Team Interactions on Multi-Robot Cooperation: A Relational Network Perspective",
    "International Symposium on Multi-Robot and Multi-Agent Systems (MRS)", "pp. 50-56, Dec. 2023",
    "10.1109/mrs60187.2023.10416779", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2023, ["Y. Piro", "C. Areias", "A. Luce", "M. Michael", "P. Biswas", "O. Ranasingha", "J. F. Reuther", "S. Trulli", "A. Akyurtlu"],
    "Low-Loss Dielectric Ink for Printed Radio Frequency and Microwave Devices",
    "ACS Applied Materials & Interfaces", "vol. 15, no. 29, pp. 35449-35458, July 2023",
    "10.1021/acsami.3c03706", "journal", ["Akyurtlu", "Ranasingha"], "Printed electronics")
pub(2023, ["Z. Zhang", "X. Wang", "S. Chen", "X. Liu", "Q. Chen", "Y. Zhang", "Y. Cao", "B. Liu"],
    "MLMSA: Multi-Level and Multi-Scale Attention for Lesion Detection in Endoscopy",
    "IEEE International Conference on E-health Networking, Application &amp; Services (Healthcom)", "pp. 144-150, Dec. 2023",
    "10.1109/healthcom56612.2023.10472340", "conference", ["Cao"], "Digital health")
pub(2023, ["D. Wang", "Y. Xu", "S. Han", "H. Yu"],
    "Masked Autoencoders for Low-dose CT Denoising",
    "IEEE 20th International Symposium on Biomedical Imaging (ISBI)", "pp. 1-4, Apr. 2023",
    "10.1109/isbi53787.2023.10230612", "conference", ["Yu"], "Medical imaging")
pub(2023, ["S. Nirgudkar", "M. DeFilippo", "M. Sacarny", "M. Benjamin", "P. Robinette"],
    "MassMIND: Massachusetts Maritime INfrared Dataset",
    "The International Journal of Robotics Research", "vol. 42, no. 1-2, pp. 21-32, Jan. 2023",
    "10.1177/02783649231153020", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2023, ["E. Lamport", "Y. Piro", "Y. Li", "A. Luce", "S. Trulli", "A. Akyurtlu"],
    "Material Selection and Process Optimizations of Additive Interconnects in Printed Circuit Boards",
    "IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (USNC-URSI)", "pp. 1787-1788, July 2023",
    "10.1109/usnc-ursi52151.2023.10237761", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["G. Cheng", "Y. Lin", "J. Yan", "J. Zhao", "L. Bai"],
    "Model-Measurement Data Integrity Attacks",
    "IEEE Transactions on Smart Grid", "vol. 14, no. 6, pp. 4741-4757, Nov. 2023",
    "10.1109/tsg.2023.3253781", "journal", ["Lin"], "Smart grid")
pub(2023, ["Y. Gao", "S. Epstein", "M. Inalpolat", "Y. N. Wu", "Y. Gu"],
    "Modeling of Interface Loads for EOD Suit Wearers",
    "IEEE/ASME International Conference on Advanced Intelligent Mechatronics (AIM)", "pp. 793-799, June 2023",
    "10.1109/aim46323.2023.10196222", "conference", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2023, ["Z. Bhuyan", "Q. Chen", "Y. Xie", "Y. Cao", "B. Liu"],
    "Modeling the Risk of Truck Rollover Crashes on Highway Ramps Using Drone Video Data and Mask-RCNN",
    "IEEE 26th International Conference on Intelligent Transportation Systems (ITSC)", "pp. 4052-4058, Sept. 2023",
    "10.1109/itsc57777.2023.10421999", "conference", ["Xie", "Cao"], "Transportation")
pub(2023, ["F. BOTTALICO", "C. NIEZRECKI", "A. SABATO"],
    "NEXT GENERATION 3D-DIC TECHNIQUE WITH SENSOR-BASED EXTRINSIC PARAMETER CALIBRATION AND NATURAL PATTERN TRACKING",
    "Proceedings of the 14th International Workshop on Structural Health Monitoring", "Sept. 2023",
    "10.12783/shm2023/36867", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["F. Chen", "H. Fu", "H. Yu", "Y. Chu"],
    "No-Reference Image Quality Assessment Based on a Multitask Image Restoration Network",
    "Applied Sciences", "vol. 13, no. 11, art. 6802, June 2023",
    "10.3390/app13116802", "journal", ["Yu"], "Medical imaging")
pub(2023, ["R. M. Osgood", "J. H. Kim", "Z. Di Zinno", "I. Uluturk", "S. Giardini", "M. Manser", "P. Brandwein", "A. Nagar", "J. Xu", "J. Plumitallo", "S. Kim", "A. Akyurtlu", "G. Strack", "S. Kooi"],
    "Novel environmentally-safe, non-toxic, and supply-chain-resilient biomaterials for optical detection of molecules",
    "Chemical, Biological, Radiological, Nuclear, and Explosives (CBRNE) Sensing XXIV", "art. 24, June 2023",
    "10.1117/12.2663793", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["S. K. Aghara", "M. Marzo"],
    "Nuclear Material Accounting and Control",
    "The Oxford Handbook of Nuclear Security", "pp. 270-287, May 2023",
    "10.1093/oxfordhb/9780192847935.013.27", "chapter", ["Aghara"], "Nuclear energy and security")
pub(2023, ["S. K. Aghara", "R. Peel"],
    "Nuclear Security for Next-Generation Reactors",
    "The Oxford Handbook of Nuclear Security", "pp. 341-357, June 2023",
    "10.1093/oxfordhb/9780192847935.013.31", "chapter", ["Aghara"], "Nuclear energy and security")
pub(2023, ["T. Nieduzak", "N. A. Valente", "C. Niezrecki", "A. Sabato"],
    "Optical Motion Magnification: A Comparative Study and Application for Vibration Analysis",
    "Conference Proceedings of the Society for Experimental Mechanics Series", "pp. 1-7, Nov. 2023",
    "10.1007/978-3-031-34910-2_1", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["E. Lamport", "A. Luce", "Y. Piro", "S. Trulli", "A. Akyurtlu"],
    "Optimization of Additively Manufactured Interposers for DC and RF Applications in Printed Circuit Boards",
    "IMAPSource Proceedings", "vol. 2022, no. IMAPS Symposium, May 2023",
    "10.4071/001c.74620", "journal", ["Akyurtlu"], "Printed electronics")
pub(2023, ["J. Yoon", "A. Moon", "S. W. Son"],
    "Outlier Elimination and Reliability Assessment for Peak and Declining Time Series Datasets",
    "IEEE International Conference on Data Mining Workshops (ICDMW)", "pp. 593-600, Dec. 2023",
    "10.1109/icdmw60847.2023.00083", "conference", ["Son"], "HPC and hardware")
pub(2023, ["A. Rezaee", "R. McCann", "V. M. Vokkarane"],
    "PLI-Aware Dynamic Routing in Software Defined Elastic Optical Networks (SD-EONs)",
    "International Conference on Optical Network Design and Modeling (ONDM)", "pp. 1-3, May 2023",
    "10.23919/ondm57372.2023.10144885", "conference", ["Vokkarane"], "Optical networks")
pub(2023, ["M. Z. Islam", "V. M. Vokkarane", "Y. Lin"],
    "PMU Network Routing for Resilient Observability of Power Grids",
    "ICC 2023 - IEEE International Conference on Communications", "pp. 4584-4590, May 2023",
    "10.1109/icc45041.2023.10279789", "conference", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["J. Chen", "S. W. Son"],
    "PSNR-Aware Quantization for DCT-based Lossy Compression",
    "IEEE International Conference on Big Data (BigData)", "pp. 4223-4232, Dec. 2023",
    "10.1109/bigdata59044.2023.10386333", "conference", ["Son"], "HPC and hardware")
pub(2023, ["S. Dabetwar", "R. Padhye", "N. N. Kulkarni", "C. Niezrecki", "A. Sabato"],
    "Performance evaluation of deep learning algorithms for heat loss damage classification in buildings from UAV-borne infrared images",
    "Journal of Building Engineering", "vol. 75, art. 106948, Sept. 2023",
    "10.1016/j.jobe.2023.106948", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["A. L. Kajenski", "G. Strack", "A. Akyurtlu"],
    "Performance of Printed Antennas on Stretchable and Non-Stretchable Textiles",
    "IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (USNC-URSI)", "pp. 949-950, July 2023",
    "10.1109/usnc-ursi52151.2023.10237906", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["T. H. Law", "S. Erol", "L. Tseng"],
    "Poster: Timestamp Verifiability in Proof-of-Work",
    "Proceedings of the Twenty-fourth International Symposium on Theory, Algorithmic Foundations, and Protocol Design for Mobile Networks and Mobile Computing", "pp. 304-305, Oct. 2023",
    "10.1145/3565287.3617934", "conference", ["Tseng"], "Distributed systems")
pub(2023, ["J. Kasule", "A. Akyurtlu", "C. Armiento"],
    "Printed, Planar Microwave Connector with Multiple Signal Lines",
    "IEEE Wireless and Microwave Technology Conference (WAMICON)", "pp. 45-48, Apr. 2023",
    "10.1109/wamicon57636.2023.10124906", "conference", ["Akyurtlu"], "Printed electronics")
pub(2023, ["O. Barut", "Y. Luo", "P. Li", "T. Zhang"],
    "R1DIT: Privacy-Preserving Malware Traffic Classification With Attention-Based Neural Networks",
    "IEEE Transactions on Network and Service Management", "vol. 20, no. 2, pp. 2071-2085, June 2023",
    "10.1109/tnsm.2022.3211254", "journal", ["Luo"], "Sensing and networks")
pub(2023, ["C. Lu", "J. Yuan", "K. Xia", "Z. Guo", "M. Chen", "H. Yu"],
    "Regional perception and multi-scale feature fusion network for cardiac segmentation",
    "Physics in Medicine & Biology", "vol. 68, no. 10, art. 105003, May 2023",
    "10.1088/1361-6560/acc71f", "journal", ["Yu"], "Medical imaging")
pub(2023, ["Z. Li", "Z. Shi", "G. Ruan", "Y. Lin", "J. Zhao"],
    "Resilience-oriented Operation of Power Distribution Networks with Line Hardening and Comprehensive Reconfiguration Measures",
    "IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)", "pp. 1-6, Oct. 2023",
    "10.1109/smartgridcomm57358.2023.10333932", "conference", ["Lin"], "Smart grid")
pub(2023, ["S. Gautam", "M. Verma", "R. Chauhan", "S. Aghara", "N. Goyal"],
    "Reviewing thermal conductivity aspects of solar salt energy storage",
    "Energy Advances", "vol. 2, no. 9, pp. 1309-1325, 2023",
    "10.1039/d3ya00274h", "journal", ["Aghara"], "Nuclear energy and security")
pub(2023, ["M. Z. Islam", "Y. Lin", "V. M. Vokkarane", "N. Yu"],
    "Robust learning-based real-time load estimation using sparsely deployed smart meters with high reporting rates",
    "Applied Energy", "vol. 352, art. 121964, Dec. 2023",
    "10.1016/j.apenergy.2023.121964", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2023, ["D. Wang", "B. Zhang", "Y. Xu", "Y. Luo", "H. Yu"],
    "SQ-Swin: Siamese Quadratic Swin Transformer for Lettuce Browning Prediction",
    "IEEE Access", "vol. 11, pp. 128724-128735, 2023",
    "10.1109/access.2023.3332488", "journal", ["Yu"], "Medical imaging")
pub(2023, ["F. Bottalico", "C. Niezrecki", "K. Jerath", "Y. Luo", "A. Sabato"],
    "Sensor-Based Calibration of Camera\u2019s Extrinsic Parameters for Stereophotogrammetry",
    "IEEE Sensors Journal", "vol. 23, no. 7, pp. 7776-7785, Apr. 2023",
    "10.1109/jsen.2023.3244413", "journal", ["Niezrecki", "Luo"], "Renewable energy and structural monitoring")
pub(2023, ["F. Bottalico", "N. A. Valente", "C. Niezrecki", "K. Jerath", "Y. Luo", "A. Sabato"],
    "Sensor-aided camera calibration for three dimensional digital image correlation measurements",
    "Health Monitoring of Structural and Biological Systems XVII", "art. 77, Apr. 2023",
    "10.1117/12.2657163", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["X. Guo", "Y. Li", "D. Chang", "P. He", "P. Feng", "H. Yu", "W. Wu"],
    "Spectral2Spectral: Image-Spectral Similarity Assisted Deep Spectral CT Reconstruction Without Reference",
    "IEEE Transactions on Computational Imaging", "vol. 9, pp. 1031-1042, 2023",
    "10.1109/tci.2023.3328278", "journal", ["Yu"], "Medical imaging")
pub(2023, ["Z. Rezaei Khavas", "M. Reddy Kotturu", "R. Purkins", "S. Reza Ahmadzadeh", "P. Robinette"],
    "The Effect of Performance-Based Compensation on Crowdsourced Human-Robot Interaction Experiments",
    "Journal of Software", "pp. 117-129, Aug. 2023",
    "10.17706/jsw.18.3.117-129", "journal", ["Robinette"], "Robotics and human-robot interaction")
pub(2023, ["E. T. Ozdemir", "M. Inalpolat", "H. K. Lee", "M. S. Kim"],
    "Three-Dimensional Steady-State and Transient Response Modelling of Geared Systems Under Stick-Slip Motion Generated Excitations",
    "Volume 11: 2023 International Power Transmission and Gearing Conference (PTG)", "Aug. 2023",
    "10.1115/detc2023-116467", "conference", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2023, ["J. Solimine", "M. Inalpolat"],
    "Unsupervised acoustic detection of fatigue-induced damage modes from wind turbine blades",
    "Wind Engineering", "vol. 47, no. 6, pp. 1116-1131, July 2023",
    "10.1177/0309524x231187152", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2023, ["F. Chen", "H. Fu", "H. Yu", "Y. Chu"],
    "Using HVS Dual-Pathway and Contrast Sensitivity to Blindly Assess Image Quality",
    "Sensors", "vol. 23, no. 10, art. 4974, May 2023",
    "10.3390/s23104974", "journal", ["Yu"], "Medical imaging")
pub(2023, ["T. B. NIEDUZAK", "N. N. KULKARNI", "C. NIEZRECKI", "A. SABATO"],
    "WIND TURBINE MONITORING USING OPTICAL MOTION MAGNIFICATION: CHALLENGES AND OPPORTUNITIES",
    "Proceedings of the 14th International Workshop on Structural Health Monitoring", "Sept. 2023",
    "10.12783/shm2023/37052", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2023, ["H. Shan", "D. Sullivan", "O. Arias"],
    "When Memory Mappings Attack: On the (Mis)use of the ARM Cortex-M FPB Unit",
    "Asian Hardware Oriented Security and Trust Symposium (AsianHOST)", "pp. 1-6, Dec. 2023",
    "10.1109/asianhost59942.2023.10409308", "conference", ["Arias"], "HPC and hardware")
pub(2023, ["S. Wang", "H. Liu", "A. Gaihre", "H. Yu"],
    "ezLDA: Efficient and Scalable LDA on GPUs",
    "IEEE Access", "vol. 11, pp. 100165-100179, 2023",
    "10.1109/access.2023.3315239", "journal", ["Yu"], "Medical imaging")
pub(2022, ["Z. Fang", "Y. Lin", "S. Song", "C. Li", "X. Lin", "F. Wang", "Y. Lu"],
    "A Comprehensive Framework for Robust AC/DC Grid State Estimation Against Measurement and Control Input Errors",
    "IEEE Transactions on Power Systems", "vol. 37, no. 2, pp. 1067-1077, Mar. 2022",
    "10.1109/tpwrs.2021.3105391", "journal", ["Lin"], "Smart grid")
pub(2022, ["G. Cheng", "Y. Lin", "J. Zhao", "J. Yan"],
    "A Highly Discriminative Detector Against False Data Injection Attacks in AC State Estimation",
    "IEEE Transactions on Smart Grid", "vol. 13, no. 3, pp. 2318-2330, May 2022",
    "10.1109/tsg.2022.3141803", "journal", ["Lin"], "Smart grid")
pub(2022, ["S. Song", "H. Wei", "Y. Lin", "C. Wang", "A. Gomez-Exposito"],
    "A Holistic State Estimation Framework for Active Distribution Network with Battery Energy Storage System",
    "Journal of Modern Power Systems and Clean Energy", "vol. 10, no. 3, pp. 627-636, 2022",
    "10.35833/mpce.2020.000613", "journal", ["Lin"], "Smart grid")
pub(2022, ["J. H. Kim", "T. Bantikyan", "N. W. Kim", "L. Tseng"],
    "A Human-centered Approach to make Networked Entertainment Green: A Case Study of CDN",
    "IEEE 42nd International Conference on Distributed Computing Systems Workshops (ICDCSW)", "pp. 227-230, July 2022",
    "10.1109/icdcsw56584.2022.00050", "conference", ["Tseng"], "Distributed systems")
pub(2022, ["E. Lamport", "A. Luce", "Y. Piro", "S. Trulli", "A. Akyurtlu"],
    "A Process for Developing Additively Manufactured Interposers for Use in Printed Circuit Boards",
    "IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (AP-S/URSI)", "pp. 1592-1593, July 2022",
    "10.1109/ap-s/usnc-ursi47032.2022.9886701", "conference", ["Akyurtlu"], "Printed electronics")
pub(2022, ["L. Zhou", "Y. Luo"],
    "A Spatio-temporal Learning for Music Conditioned Dance Generation",
    "Proceedings of the 2022 International Conference on Multimodal Interaction", "pp. 57-62, Nov. 2022",
    "10.1145/3536221.3556618", "conference", ["Luo"], "Sensing and networks")
pub(2022, ["A. S. Sushmit", "Y. Xu", "O. Mariani", "Q. Lyu", "Y. Li", "X. Cao", "C. Wiedeman", "H. Ma", "J. Maltz", "H. Yu", "G. Wang"],
    "A data generation pipeline for cardiac vessel segmentation and motion artifact grading",
    "Developments in X-Ray Tomography XIV", "art. 61, Nov. 2022",
    "10.1117/12.2642869", "conference", ["Yu"], "Medical imaging")
pub(2022, ["F. Bottalico", "N. A. Valente", "S. Dabetwar", "K. Jerath", "Y. Luo", "C. Niezrecki", "A. Sabato"],
    "A sensor-based calibration system for three-dimensional digital image correlation",
    "Health Monitoring of Structural and Biological Systems XVI", "art. 54, Apr. 2022",
    "10.1117/12.2612106", "conference", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["D. Wang", "S. Chen", "X. Sun", "Q. Chen", "Y. Cao", "B. Liu", "X. Liu"],
    "AFP-Mask: Anchor-Free Polyp Instance Segmentation in Colonoscopy",
    "IEEE Journal of Biomedical and Health Informatics", "vol. 26, no. 7, pp. 2995-3006, July 2022",
    "10.1109/jbhi.2022.3147686", "journal", ["Cao"], "Digital health")
pub(2022, ["A. Sabato", "C. Niezrecki", "S. Dabetwar", "N. N. Kulkarni", "F. Bottalico", "T. Nieduzak"],
    "Advancements in Structural Health Monitoring Using Combined Computer-Vision and Unmanned Aerial Vehicles Approaches",
    "Lecture Notes in Civil Engineering", "pp. 417-426, June 2022",
    "10.1007/978-3-031-07258-1_43", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["J. Solimine", "M. Inalpolat"],
    "An unsupervised data-driven approach for wind turbine blade damage detection under passive acoustics-based excitation",
    "Wind Engineering", "vol. 46, no. 4, pp. 1311-1330, Feb. 2022",
    "10.1177/0309524x221080470", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2022, ["S. Wang", "M. Yang", "T. Ge", "Y. Luo", "X. Fu"],
    "BBS: A Blockchain Big-Data Sharing System",
    "ICC 2022 - IEEE International Conference on Communications", "pp. 4205-4210, May 2022",
    "10.1109/icc45855.2022.9838666", "conference", ["Luo"], "Sensing and networks")
pub(2022, ["L. Tseng", "Q. Zhang"],
    "Brief Announcement: Computability and Anonymous Storage-Efficient Consensus with an Abstract MAC Layer",
    "Proceedings of the 2022 ACM Symposium on Principles of Distributed Computing", "pp. 265-267, July 2022",
    "10.1145/3519270.3538462", "conference", ["Tseng"], "Distributed systems")
pub(2022, ["A. Du", "Y. Shen", "Q. Zhang", "L. Tseng", "M. Aloqaily"],
    "CRACAU: Byzantine Machine Learning Meets Industrial Edge Computing in Industry 5.0",
    "IEEE Transactions on Industrial Informatics", "vol. 18, no. 8, pp. 5435-5445, Aug. 2022",
    "10.1109/tii.2021.3097072", "journal", ["Tseng"], "Distributed systems")
pub(2022, ["Y. Xu", "A. Sushmit", "Q. Lyu", "Y. Li", "X. Cao", "J. S. Maltz", "G. Wang", "H. Yu"],
    "Cardiac CT motion artifact grading via semi-automatic labeling and vessel tracking using synthetic image-augmented training data",
    "Journal of X-Ray Science and Technology", "vol. 30, no. 3, pp. 433-445, Apr. 2022",
    "10.3233/xst-211109", "journal", ["Yu"], "Medical imaging")
pub(2022, ["A. Moon", "J. Chen", "S. W. Son", "M. Kim"],
    "Characterization of Transform-Based Lossy Compression for HPC Datasets",
    "IEEE/ACM 8th International Workshop on Data Analysis and Reduction for Big Scientific Data (DRBSD)", "pp. 56-62, Nov. 2022",
    "10.1109/drbsd56682.2022.00013", "conference", ["Son"], "HPC and hardware")
pub(2022, ["D. Shen", "C. Dumas", "C. Sardina", "L. Tseng", "M. Aloqaily"],
    "Cholula: Fast, Fault-tolerant, and Strongly Consistent Off-chain Object Storage",
    "Fourth International Conference on Blockchain Computing and Applications (BCCA)", "pp. 189-194, Sept. 2022",
    "10.1109/bcca55292.2022.9922577", "conference", ["Tseng"], "Distributed systems")
pub(2022, ["C. Areias", "E. Lamport", "Y. Piro", "M. Cason", "C. Armiento", "A. Akyurtlu"],
    "Comparison of Additive Manufacturing Methods for the Attachment of Bare Die to Printed Circuit Boards",
    "IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (AP-S/URSI)", "pp. 1056-1057, July 2022",
    "10.1109/ap-s/usnc-ursi47032.2022.9886376", "conference", ["Akyurtlu"], "Printed electronics")
pub(2022, ["C. Traylor", "M. Inalpolat"],
    "Computational investigation into the effect of material properties on aeroacoustics based damage detection from wind turbine blades",
    "INTER-NOISE and NOISE-CON Congress and Conference Proceedings", "vol. 264, no. 1, pp. 317-327, June 2022",
    "10.3397/nc-2022-736", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2022, ["X. Zhuo", "W. Rahfeldt", "X. Zhang", "T. Doros", "S. W. Son"],
    "DAP-SDD: Distribution-Aware Pseudo Labeling for Small Defect Detection",
    "AAAI Workshop on Artificial Intelligence with Biased or Scarce Data (AIBSD)", "art. 5, Apr. 2022",
    "10.3390/cmsf2022003005", "conference", ["Son"], "HPC and hardware")
pub(2022, ["C. Niezrecki", "P. L. Reu", "J. Baqersad", "D. P. Rohe"],
    "DIC and Photogrammetry for Structural Dynamic Analysis and High-Speed Testing",
    "Handbook of Experimental Structural Dynamics", "pp. 409-478, 2022",
    "10.1007/978-1-4614-4547-0_3", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["X. Sun", "Y. Xie", "L. Jiang", "Y. Cao", "B. Liu"],
    "DMA-Net: DeepLab With Multi-Scale Attention for Pavement Crack Segmentation",
    "IEEE Transactions on Intelligent Transportation Systems", "vol. 23, no. 10, pp. 18392-18403, Oct. 2022",
    "10.1109/tits.2022.3158670", "journal", ["Xie", "Cao"], "Transportation")
pub(2022, ["Z. Xiong", "Q. Chen", "C. Zhang", "Y. Cao", "B. Liu", "Y. Wu", "Y. Peng", "X. Liu"],
    "Deep Learning Assisted Mouth-Esophagus Passage Time Estimation During Gastroscopy",
    "IEEE 34th International Conference on Tools with Artificial Intelligence (ICTAI)", "Oct. 2022",
    "10.1109/ictai56018.2022.00169", "conference", ["Cao"], "Digital health")
pub(2022, ["J. Ni", "Z. Bhuyan", "Q. Chen", "X. Sun", "D. Wang", "Y. Cao", "B. Liu"],
    "Enhance Chest X-ray Classification with Multi-image Fusion and Pseudo-3D Reconstruction",
    "International Joint Conference on Neural Networks (IJCNN)", "pp. 1-8, July 2022",
    "10.1109/ijcnn55064.2022.9892095", "conference", ["Cao"], "Digital health")
pub(2022, ["V. K. Garg", "S. Kumar", "L. Tseng", "X. Zheng"],
    "Fault-tolerant Snapshot Objects in Message Passing Systems",
    "IEEE International Parallel and Distributed Processing Symposium (IPDPS)", "pp. 1129-1139, May 2022",
    "10.1109/ipdps53621.2022.00113", "conference", ["Tseng"], "Distributed systems")
pub(2022, ["C. Lu", "Z. Guo", "J. Yuan", "K. Xia", "H. Yu"],
    "Fine-grained calibrated double-attention convolutional network for left ventricular segmentation",
    "Physics in Medicine & Biology", "vol. 67, no. 5, art. 055013, Mar. 2022",
    "10.1088/1361-6560/ac5570", "journal", ["Yu"], "Medical imaging")
pub(2022, ["K. Chen", "O. Arias", "Q. Deng", "D. Oliveira", "X. Guo", "Y. Jin"],
    "FineDIFT: Fine-Grained Dynamic Information Flow Tracking for Data-Flow Integrity Using Coprocessor",
    "IEEE Transactions on Information Forensics and Security", "vol. 17, pp. 559-573, 2022",
    "10.1109/tifs.2022.3144868", "journal", ["Arias"], "HPC and hardware")
pub(2022, ["T. Li", "D. Chen", "H. Zhou", "Y. Xie", "J. Laval"],
    "Fundamental diagrams of commercial adaptive cruise control: Worldwide experimental evidence",
    "Transportation Research Part C: Emerging Technologies", "vol. 134, art. 103458, Jan. 2022",
    "10.1016/j.trc.2021.103458", "journal", ["Xie"], "Transportation")
pub(2022, ["W. Fu", "H. Yu", "O. Arias", "K. Yang", "Y. Jin", "T. Yavuz", "X. Guo"],
    "Graph Neural Network based Hardware Trojan Detection at Intermediate Representative for SoC Platforms",
    "Proceedings of the Great Lakes Symposium on VLSI 2022", "pp. 481-486, June 2022",
    "10.1145/3526241.3530827", "conference", ["Arias"], "HPC and hardware")
pub(2022, ["Y. Chu", "F. Chen", "H. Fu", "H. Yu"],
    "Haze Level Evaluation Using Dark and Bright Channel Prior Information",
    "Atmosphere", "vol. 13, no. 5, art. 683, Apr. 2022",
    "10.3390/atmos13050683", "journal", ["Yu"], "Medical imaging")
pub(2022, ["Z. Liu", "O. Arias", "W. Fu", "Y. Jin", "X. Guo"],
    "Inter-IP Malicious Modification Detection through Static Information Flow Tracking",
    "Design, Automation & Test in Europe Conference & Exhibition (DATE)", "pp. 600-603, Mar. 2022",
    "10.23919/date54114.2022.9774694", "conference", ["Arias"], "HPC and hardware")
pub(2022, ["H. Kong", "X. Lian", "J. Pan", "H. Yu"],
    "Joint multi-channel total generalized variation minimization and tensor decomposition for spectral CT reconstruction",
    "7th International Conference on Image Formation in X-Ray Computed Tomography", "art. 81, Oct. 2022",
    "10.1117/12.2646976", "conference", ["Yu"], "Medical imaging")
pub(2022, ["A. Moon", "S. W. Son", "H. Kim", "M. Kim"],
    "Lossy Predictive Models for Accurate Classification Algorithms",
    "IEEE International Conference on Big Data (Big Data)", "pp. 4576-4582, Dec. 2022",
    "10.1109/bigdata55660.2022.10020381", "conference", ["Son"], "HPC and hardware")
pub(2022, ["Z. Guo", "L. Zhao", "J. Yuan", "H. Yu"],
    "MSANet: Multiscale Aggregation Network Integrating Spatial and Channel Information for Lung Nodule Detection",
    "IEEE Journal of Biomedical and Health Informatics", "vol. 26, no. 6, pp. 2547-2558, June 2022",
    "10.1109/jbhi.2021.3131671", "journal", ["Yu"], "Medical imaging")
pub(2022, ["G. Strack", "Y. AitElAoud", "R. M. Osgood", "A. Akyurtlu"],
    "Magnetic nanoarrays on flexible substrates",
    "MRS Advances", "vol. 7, no. 20, pp. 410-414, Jan. 2022",
    "10.1557/s43580-021-00193-z", "journal", ["Akyurtlu"], "Printed electronics")
pub(2022, ["P. Robinson", "L. Sun", "H. Furey", "R. Jenkins", "C. R. M. Phillips", "T. M. Powers", "R. S. Ritterson", "Y. Xie", "R. Casagrande", "N. G. Evans"],
    "Modelling Ethical Algorithms in Autonomous Vehicles Using Crash Data",
    "IEEE Transactions on Intelligent Transportation Systems", "vol. 23, no. 7, pp. 7775-7784, July 2022",
    "10.1109/tits.2021.3072792", "journal", ["Xie"], "Transportation")
pub(2022, ["Y. Zou", "T. Zhu", "Y. Xie", "Y. Zhang", "Y. Zhang"],
    "Multivariate analysis of car-following behavior data using a coupled hidden Markov model",
    "Transportation Research Part C: Emerging Technologies", "vol. 144, art. 103914, Nov. 2022",
    "10.1016/j.trc.2022.103914", "journal", ["Xie"], "Transportation")
pub(2022, ["M. Yang", "Y. Luo", "A. Sharma", "Z. Jia", "S. Wang", "D. Wang", "S. Lin", "W. Perreault", "S. Purohit", "T. Gu", "H. Dillow", "X. Liu", "H. Yu", "B. Zhang"],
    "Nondestructive and multiplex differentiation of pathogenic microorganisms from spoilage microflora on seafood using paper chromogenic array and neural network",
    "Food Research International", "vol. 162, art. 112052, Dec. 2022",
    "10.1016/j.foodres.2022.112052", "journal", ["Yu"], "Medical imaging")
pub(2022, ["F. L. Fan", "D. Wang", "H. Guo", "Q. Zhu", "P. Yan", "G. Wang", "H. Yu"],
    "On a Sparse Shortcut Topology of Artificial Neural Networks",
    "IEEE Transactions on Artificial Intelligence", "vol. 3, no. 4, pp. 595-608, Aug. 2022",
    "10.1109/tai.2021.3128132", "journal", ["Yu"], "Medical imaging")
pub(2022, ["X. Wen", "Y. Xie", "L. Jiang", "Y. Li", "T. Ge"],
    "On the interpretability of machine learning methods in crash frequency modeling and crash modification factor development",
    "Accident Analysis & Prevention", "vol. 168, art. 106617, Apr. 2022",
    "10.1016/j.aap.2022.106617", "journal", ["Xie"], "Transportation")
pub(2022, ["K. Berry", "E. M. Brown", "B. Pothier", "S. Fedorka", "A. Akyurtlu", "C. Armiento", "G. F. Walsh", "C. Shemelya"],
    "Overcoming Variability in Printed RF: A Statistical Method to Designing for Unpredictable Dimensionality",
    "Designs", "vol. 6, no. 1, art. 13, Feb. 2022",
    "10.3390/designs6010013", "journal", ["Akyurtlu"], "Printed electronics")
pub(2022, ["M. Deng", "P. A. Guerron-Quintana", "L. Tseng"],
    "Parallel Computation of Sovereign Default Models",
    "Computational Economics", "vol. 62, no. 3, pp. 1047-1085, Oct. 2022",
    "10.1007/s10614-022-10291-1", "journal", ["Tseng"], "Distributed systems")
pub(2022, ["E. Meriaux", "D. Koehler", "M. Z. Islam", "V. Vokkarane", "Y. Lin"],
    "Performance Comparison of Machine Learning Methods in DDoS Attack Detection in Smart Grids",
    "IEEE MIT Undergraduate Research Technology Conference (URTC)", "pp. 1-5, Sept. 2022",
    "10.1109/urtc56832.2022.10002244", "conference", ["Vokkarane", "Lin"], "Optical networks")
pub(2022, ["Y. Jia", "Y. Liu", "B. Wang", "D. Lu", "Y. Lin"],
    "Power Network Fault Location with Exact Distributed Parameter Line Model and Sparse Estimation",
    "Electric Power Systems Research", "vol. 212, art. 108137, Nov. 2022",
    "10.1016/j.epsr.2022.108137", "journal", ["Lin"], "Smart grid")
pub(2022, ["A. Kajenski", "S. Khushrushahi", "G. Strack", "A. Akyurtlu"],
    "Printed Metasurfaces for Wearables",
    "IEEE International Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting (AP-S/URSI)", "pp. 557-558, July 2022",
    "10.1109/ap-s/usnc-ursi47032.2022.9887270", "conference", ["Akyurtlu"], "Printed electronics")
pub(2022, ["J. Kasule", "S. G. Rohani", "M. Pothier", "Y. Piro", "A. Akyurtlu", "C. Armiento"],
    "Printed Microwave Connector",
    "IEEE 72nd Electronic Components and Technology Conference (ECTC)", "pp. 2184-2190, May 2022",
    "10.1109/ectc51906.2022.00345", "conference", ["Akyurtlu"], "Printed electronics")
pub(2022, ["N. A. Valente", "C. T. do Cabo", "Z. Mao", "C. Niezrecki"],
    "Quantification of phase-based magnified motion using image enhancement and optical flow techniques",
    "Measurement", "vol. 189, art. 110508, Feb. 2022",
    "10.1016/j.measurement.2021.110508", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["O. Arias", "Z. Liu", "X. Guo", "Y. Jin", "S. Wang"],
    "RTSEC: Automated RTL Code Augmentation for Hardware Security Enhancement",
    "Design, Automation & Test in Europe Conference & Exhibition (DATE)", "pp. 596-599, Mar. 2022",
    "10.23919/date54114.2022.9774745", "conference", ["Arias"], "HPC and hardware")
pub(2022, ["J. H. Kim", "G. Strack", "A. Akyurtlu", "R. M. Osgood"],
    "Reconfigurable magnetic diodes for rectification (Conference Presentation)",
    "Metamaterials, Metadevices, and Metasystems 2022", "art. 60, Oct. 2022",
    "10.1117/12.2633328", "conference", ["Akyurtlu"], "Printed electronics")
pub(2022, ["L. Jiang", "Y. Xie", "N. G. Evans", "X. Wen", "T. Li", "D. Chen"],
    "Reinforcement Learning based cooperative longitudinal control for reducing traffic oscillations and improving platoon stability",
    "Transportation Research Part C: Emerging Technologies", "vol. 141, art. 103744, Aug. 2022",
    "10.1016/j.trc.2022.103744", "journal", ["Xie"], "Transportation")
pub(2022, ["Y. Wu", "Y. Shen", "H. Pan", "L. Tseng", "M. Aloqaily"],
    "Reliable Broadcast in Critical Applications: Asset Transfer and Smart Home",
    "ICC 2022 - IEEE International Conference on Communications", "pp. 5286-5291, May 2022",
    "10.1109/icc45855.2022.9838701", "conference", ["Tseng"], "Distributed systems")
pub(2022, ["B. Sarikaya", "M. Inalpolat"],
    "Response Sensitivity of Centrifugal Pendulum Vibration Absorbers to Symmetry-Breaking Absorber Imperfections",
    "Journal of Sound and Vibration", "vol. 535, art. 117037, Sept. 2022",
    "10.1016/j.jsv.2022.117037", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2022, ["C. Liu", "C. Wang", "Y. Lin", "T. Bi"],
    "Robust Unit Commitment of Integrated Electric-Heat Systems With Weather Parameter Driven Uncertainties",
    "IEEE Systems Journal", "vol. 16, no. 3, pp. 4641-4652, Sept. 2022",
    "10.1109/jsyst.2021.3110860", "journal", ["Lin"], "Smart grid")
pub(2022, ["S. Song", "H. Xiong", "Y. Lin", "M. Huang", "Z. Wei", "Z. Fang"],
    "Robust three-phase state estimation for PV-Integrated unbalanced distribution systems",
    "Applied Energy", "vol. 322, art. 119427, Sept. 2022",
    "10.1016/j.apenergy.2022.119427", "journal", ["Lin"], "Smart grid")
pub(2022, ["M. Zakeri", "S. Aghara", "A. Mishra", "L. Annadevula"],
    "SMRs and Thermal Energy Storage on Decommissioned Nuclear Sites",
    "Transactions of the American Nuclear Society", "vol. 127, pp. 60-63, 2022",
    "10.13182/t130-39642", "conference", ["Aghara"], "Nuclear energy and security")
pub(2022, ["S. Dabetwar", "N. N. Kulkarni", "M. Angelosanti", "C. Niezrecki", "A. Sabato"],
    "Sensitivity analysis of unmanned aerial vehicle-borne 3D point cloud reconstruction from infrared images",
    "Journal of Building Engineering", "vol. 58, art. 105070, Oct. 2022",
    "10.1016/j.jobe.2022.105070", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["Y. Piro", "A. Luce", "O. K. Ranasingha", "C. Armiento", "A. Akyurtlu"],
    "Stabilizing Selective Laser-Sintered Silver\u2013Barium Strontium Titanate (Ag-BST) Resistors Using a UV-Curable Ink",
    "Journal of Electronic Materials", "vol. 52, no. 2, pp. 1169-1176, Nov. 2022",
    "10.1007/s11664-022-10049-3", "journal", ["Akyurtlu", "Ranasingha"], "Printed electronics")
pub(2022, ["W. Wu", "D. Hu", "W. Cong", "H. Shan", "S. Wang", "C. Niu", "P. Yan", "H. Yu", "V. Vardhanabhuti", "G. Wang"],
    "Stabilizing deep tomographic reconstruction: Part A. Hybrid framework and experimental results",
    "Patterns", "vol. 3, no. 5, art. 100474, May 2022",
    "10.1016/j.patter.2022.100474", "journal", ["Yu"], "Medical imaging")
pub(2022, ["W. Wu", "D. Hu", "W. Cong", "H. Shan", "S. Wang", "C. Niu", "P. Yan", "H. Yu", "V. Vardhanabhuti", "G. Wang"],
    "Stabilizing deep tomographic reconstruction: Part B. Convergence analysis and adversarial attacks",
    "Patterns", "vol. 3, no. 5, art. 100475, May 2022",
    "10.1016/j.patter.2022.100475", "journal", ["Yu"], "Medical imaging")
pub(2022, ["J. Zhao", "V. M. Vokkarane"],
    "Static multi-sourced data retrieval in elastic optical networks",
    "Journal of Optical Communications and Networking", "vol. 14, no. 10, art. 792, Sept. 2022",
    "10.1364/jocn.465019", "journal", ["Vokkarane"], "Optical networks")
pub(2022, ["N. A. Valente", "A. Sarrafi", "Z. Mao", "C. Niezrecki"],
    "Streamlined particle filtering of phase-based magnified videos for quantified operational deflection shapes",
    "Mechanical Systems and Signal Processing", "vol. 177, art. 109233, Sept. 2022",
    "10.1016/j.ymssp.2022.109233", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["Z. Xiong", "C. Wang", "Y. Li", "Y. Luo", "Y. Cao"],
    "Swin-Pose: Swin Transformer Based Human Pose Estimation",
    "IEEE 5th International Conference on Multimedia Information Processing and Retrieval (MIPR)", "pp. 228-233, Aug. 2022",
    "10.1109/mipr54900.2022.00048", "conference", ["Luo", "Cao"], "Sensing and networks")
pub(2022, ["N. A. Valente", "C. T. do Cabo", "Z. Mao", "C. Niezrecki"],
    "Template Matching and Particle Filtering for Structural Identification of High- and Low-Frequency Vibration",
    "Conference Proceedings of the Society for Experimental Mechanics Series", "pp. 43-50, July 2022",
    "10.1007/978-3-031-04098-6_5", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["R. Perkins", "Z. R. Khavas", "K. McCallum", "M. R. Kotturu", "P. Robinette"],
    "The Reason for an Apology Matters for Robot Trust Repair",
    "Lecture Notes in Computer Science", "pp. 640-651, 2022",
    "10.1007/978-3-031-24670-8_56", "chapter", ["Robinette"], "Robotics and human-robot interaction")
pub(2022, ["B. Hammerstrom", "C. Niezrecki", "K. Hellman", "X. Jin", "M. B. Ross", "J. H. Mack", "E. Agar", "J. P. Trelles", "F. Liu", "F. Che", "D. Ryan", "M. S. Narasimhadevara", "M. Usovicz"],
    "The viability of implementing hydrogen in the Commonwealth of Massachusetts",
    "Frontiers in Energy Research", "vol. 10, Sept. 2022",
    "10.3389/fenrg.2022.1005101", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2022, ["J. Chen", "A. Moon", "S. W. Son"],
    "Towards Guaranteeing Error Bound in DCT-based Lossy Compression",
    "IEEE International Conference on Big Data (Big Data)", "pp. 3139-3145, Dec. 2022",
    "10.1109/bigdata55660.2022.10020345", "conference", ["Son"], "HPC and hardware")
pub(2022, ["M. Wu", "P. FitzGerald", "J. Zhang", "W. P. Segars", "H. Yu", "Y. Xu", "B. De Man"],
    "XCIST\u2014an open access x-ray/CT simulation toolkit",
    "Physics in Medicine & Biology", "vol. 67, no. 19, art. 194002, Sept. 2022",
    "10.1088/1361-6560/ac9174", "journal", ["Yu"], "Medical imaging")
pub(2022, ["T. Griffin", "Q. Chen", "X. Sun", "D. Wang", "M. J. Brunette", "Y. Cao", "B. Liu"],
    "eRxNet: A Pipeline of Convolutional Neural Networks for Tuberculosis Screening",
    "International Journal of Semantic Computing", "vol. 16, no. 01, pp. 69-92, Mar. 2022",
    "10.1142/s1793351x22400049", "journal", ["Cao"], "Digital health")
pub(2021, ["M. Inalpolat", "E. T. Ozdemir"],
    "A dynamic shell model for diagnostics of rotating machinery under periodic excitation",
    "INTER-NOISE and NOISE-CON Congress and Conference Proceedings", "vol. 263, no. 2, pp. 4120-4131, Aug. 2021",
    "10.3397/in-2021-2605", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2021, ["C. Traylor", "M. Inalpolat"],
    "A generalized computational approach to predict high-frequency acoustic pressure response of cavity structures for structural health monitoring of wind turbine blades",
    "Wind Engineering", "vol. 46, no. 3, pp. 914-937, Dec. 2021",
    "10.1177/0309524x211060552", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2021, ["E. T. Ozdemir", "B. Sarikaya", "M. Inalpolat", "H. K. Lee", "M. S. Kim"],
    "A multibody dynamic model for predicting operational load spectra of dual clutch transmissions",
    "INTER-NOISE and NOISE-CON Congress and Conference Proceedings", "vol. 263, no. 2, pp. 4132-4143, Aug. 2021",
    "10.3397/in-2021-2609", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2021, ["C. Wang", "Y. Xie", "H. Huang", "P. Liu"],
    "A review of surrogate safety measures and their applications in connected and automated vehicles safety modeling",
    "Accident Analysis & Prevention", "vol. 157, art. 106157, July 2021",
    "10.1016/j.aap.2021.106157", "journal", ["Xie"], "Transportation")
pub(2021, ["G. Cheng", "Y. Lin", "Y. Chen", "T. Bi"],
    "Adaptive State Estimation for Power Systems Measured by PMUs With Unknown and Time-Varying Error Statistics",
    "IEEE Transactions on Power Systems", "vol. 36, no. 5, pp. 4482-4491, Sept. 2021",
    "10.1109/tpwrs.2021.3055189", "journal", ["Lin"], "Smart grid")
pub(2021, ["B. Sarikaya", "E. T. Ozdemir", "M. Inalpolat", "H. K. Lee", "M. S. Kim"],
    "An analytical model for predicting noise radiated by switch reluctance electric motors",
    "INTER-NOISE and NOISE-CON Congress and Conference Proceedings", "vol. 263, no. 2, pp. 4100-4110, Aug. 2021",
    "10.3397/in-2021-2601", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2021, ["A. R. Wagner", "P. Robinette"],
    "An explanation is not an excuse: Trust calibration in an age of transparent robots",
    "Trust in Human-Robot Interaction", "pp. 197-208, 2021",
    "10.1016/b978-0-12-819472-0.00009-5", "chapter", ["Robinette"], "Robotics and human-robot interaction")
pub(2021, ["X. Wen", "Y. Xie", "L. Jiang", "Z. Pu", "T. Ge"],
    "Applications of machine learning methods in traffic crash severity modelling: current status and future directions",
    "Transport Reviews", "vol. 41, no. 6, pp. 855-879, July 2021",
    "10.1080/01441647.2021.1954108", "journal", ["Xie"], "Transportation")
pub(2021, ["D. A. Abbink", "P. Hao", "J. Laval", "S. Shalev-Shwartz", "C. Wu", "T. Yang", "S. Hamdar", "D. Chen", "Y. Xie", "X. Li", "M. Haque"],
    "Artificial Intelligence for Automated Vehicle Control and Traffic Operations: Challenges and Opportunities",
    "Lecture Notes in Mobility", "pp. 60-72, July 2021",
    "10.1007/978-3-030-80063-5_6", "chapter", ["Xie"], "Transportation")
pub(2021, ["Z. Wu", "R. Ge", "Y. Chen", "X. He", "L. Luo", "Y. Cao", "H. Yu"],
    "Automatic Patient-Level Detection of Coronavirus Disease (COVID-19) Using Convolutional Neural Network from Lung CT Scans",
    "Journal of Medical Imaging and Health Informatics", "vol. 11, no. 11, pp. 2722-2732, Nov. 2021",
    "10.1166/jmihi.2021.3865", "journal", ["Yu"], "Medical imaging")
pub(2021, ["G. Bejerano", "P. Robinette", "H. A. Yanco", "E. Phillips"],
    "Back to the Future: Opinions of Autonomous Cars Over Time",
    "Companion of the 2021 ACM/IEEE International Conference on Human-Robot Interaction", "pp. 157-161, Mar. 2021",
    "10.1145/3434074.3447150", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2021, ["S. Nirgudkar", "P. Robinette"],
    "Beyond Visible Light: Usage of Long Wave Infrared for Object Detection in Maritime Environment",
    "20th International Conference on Advanced Robotics (ICAR)", "pp. 1093-1100, Dec. 2021",
    "10.1109/icar53236.2021.9659477", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2021, ["Y. Zhang", "D. Hu", "Q. Zhao", "G. Quan", "J. Liu", "Q. Liu", "Y. Zhang", "G. Coatrieux", "Y. Chen", "H. Yu"],
    "CLEAR: Comprehensive Learning Enabled Adversarial Reconstruction for Subtle Structure Enhanced Low-Dose CT Imaging",
    "IEEE Transactions on Medical Imaging", "vol. 40, no. 11, pp. 3089-3101, Nov. 2021",
    "10.1109/tmi.2021.3097808", "journal", ["Yu"], "Medical imaging")
pub(2021, ["M. Oumano", "L. Russell", "M. Salehjahromi", "L. Shanshan", "N. Sinha", "W. Ngwa", "H. Yu"],
    "CT imaging of gold nanoparticles in a human\u2010sized phantom",
    "Journal of Applied Clinical Medical Physics", "vol. 22, no. 1, pp. 337-342, Jan. 2021",
    "10.1002/acm2.13155", "journal", ["Yu"], "Medical imaging")
pub(2021, ["T. Li", "D. Chen", "H. Zhou", "J. Laval", "Y. Xie"],
    "Car-following behavior characteristics of adaptive cruise control vehicles based on empirical experiments",
    "Transportation Research Part B: Methodological", "vol. 147, pp. 67-91, May 2021",
    "10.1016/j.trb.2021.03.003", "journal", ["Xie"], "Transportation")
pub(2021, ["X. Zhuo", "A. Moon", "J. Zhang", "S. W. Son"],
    "Cascaded Dimension Reduction for Effective Anomaly Detection",
    "IEEE International Conference on Big Data (Big Data)", "pp. 4480-4490, Dec. 2021",
    "10.1109/bigdata52589.2021.9671364", "conference", ["Son"], "HPC and hardware")
pub(2021, ["J. Strandburg", "C. Duffley", "S. Aghara"],
    "Creation of a Condenser Testbed for Hardware in the Loop Testing Using the Asherah Simulator",
    "12th Nuclear Plant Instrumentation, Control and Human-Machine Interface Technologies (NPIC&HMIT 2021)", "pp. 925-832, 2021",
    "10.13182/t124-36078", "conference", ["Aghara"], "Nuclear energy and security")
pub(2021, ["J. Zhang", "J. Chen", "X. Zhuo", "A. Moon", "S. W. Son"],
    "DPZ: Improving Lossy Compression Ratio with Information Retrieval on Scientific Data",
    "IEEE International Conference on Cluster Computing (CLUSTER)", "pp. 320-331, Sept. 2021",
    "10.1109/cluster48925.2021.00056", "conference", ["Son"], "HPC and hardware")
pub(2021, ["W. Wu", "D. Hu", "C. Niu", "H. Yu", "V. Vardhanabhuti", "G. Wang"],
    "DRONE: Dual-Domain Residual-based Optimization NEtwork for Sparse-View CT Reconstruction",
    "IEEE Transactions on Medical Imaging", "vol. 40, no. 11, pp. 3002-3014, Nov. 2021",
    "10.1109/tmi.2021.3078067", "journal", ["Yu"], "Medical imaging")
pub(2021, ["L. Jiang", "Y. Xie", "X. Wen", "D. Chen", "T. Li", "N. G. Evans"],
    "Dampen the Stop-and-Go Traffic with Connected and Automated Vehicles \u2013 A Deep Reinforcement Learning Approach",
    "7th International Conference on Models and Technologies for Intelligent Transportation Systems (MT-ITS)", "pp. 1-6, June 2021",
    "10.1109/mt-its49943.2021.9529289", "conference", ["Xie"], "Transportation")
pub(2021, ["Y. Chen", "H. Chen", "Y. Jiao", "J. Ma", "Y. Lin"],
    "Data-driven Robust State Estimation Through Off-line Learning and On-line Matching",
    "Journal of Modern Power Systems and Clean Energy", "vol. 9, no. 4, pp. 897-909, 2021",
    "10.35833/mpce.2020.000835", "journal", ["Lin"], "Smart grid")
pub(2021, ["L. Zhou", "Y. Luo"],
    "Deep Features Fusion with Mutual Attention Transformer for Skin Lesion Diagnosis",
    "IEEE International Conference on Image Processing (ICIP)", "pp. 3797-3801, Sept. 2021",
    "10.1109/icip42928.2021.9506211", "conference", ["Luo"], "Sensing and networks")
pub(2021, ["P. Afsharlar", "A. Deylamsalehi", "V. M. Vokkarane"],
    "Delayed spectrum allocation in elastic optical networks with anycast traffic",
    "OSA Continuum", "vol. 4, no. 8, art. 2118, July 2021",
    "10.1364/osac.414698", "journal", ["Vokkarane"], "Optical networks")
pub(2021, ["T. Clunie", "M. DeFilippo", "M. Sacarny", "P. Robinette"],
    "Development of a Perception System for an Autonomous Surface Vehicle using Monocular Camera, LIDAR, and Marine RADAR",
    "IEEE International Conference on Robotics and Automation (ICRA)", "pp. 14112-14119, May 2021",
    "10.1109/icra48506.2021.9561275", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2021, ["A. Du", "Y. Shen", "L. Tseng", "T. Higuchi", "S. Ucar", "O. Altintas"],
    "Enabling Pervasive Federated Learning using Vehicular Virtual Edge Servers",
    "IEEE International Conference on Pervasive Computing and Communications Workshops and other Affiliated Events (PerCom Workshops)", "pp. 324-327, Mar. 2021",
    "10.1109/percomworkshops51409.2021.9430863", "conference", ["Tseng"], "Distributed systems")
pub(2021, ["A. Abur", "M. G\u00f6l", "Y. Lin"],
    "Estimating the System State and Network Model Errors",
    "Advanced Data Analytics for Power Systems", "pp. 74-98, Jan. 2021",
    "10.1017/9781108859806.006", "chapter", ["Lin"], "Smart grid")
pub(2021, ["J. Boffie", "S. Aghara", "O. Dim", "J. Strandburg"],
    "Estimation of the fuel temperature reactivity coefficient of the UMass-Lowell research reactor based on empirical and theoretical point reactor kinetics models",
    "Nuclear Engineering and Design", "vol. 381, art. 111341, Sept. 2021",
    "10.1016/j.nucengdes.2021.111341", "journal", ["Aghara"], "Nuclear energy and security")
pub(2021, ["R. K. Gondle", "P. U. Kurup", "C. Niezrecki"],
    "Evaluation of Wind Turbine-Foundation Degradation",
    "Lecture Notes in Civil Engineering", "pp. 21-28, 2021",
    "10.1007/978-3-030-64518-2_3", "chapter", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2021, ["J. Posner", "L. Tseng", "M. Aloqaily", "Y. Jararweh"],
    "Federated Learning in Vehicular Networks: Opportunities and Solutions",
    "IEEE Network", "vol. 35, no. 2, pp. 152-159, Mar. 2021",
    "10.1109/mnet.011.2000430", "journal", ["Tseng"], "Distributed systems")
pub(2021, ["O. K. Ranasingha", "M. Haghzadeh", "M. J. Sobkowicz", "E. Kingsley", "C. Armiento", "A. Akyurtlu"],
    "Formulation and Characterization of Sinterless Barium Strontium Titanate (BST) Dielectric Nanoparticle Ink for Printed RF and Microwave Applications",
    "Journal of Electronic Materials", "vol. 50, no. 6, pp. 3241-3248, Apr. 2021",
    "10.1007/s11664-021-08915-7", "journal", ["Akyurtlu", "Ranasingha"], "Printed electronics")
pub(2021, ["W. Fu", "O. Arias", "Y. Jin", "X. Guo"],
    "Fuzzing Hardware: Faith or Reality? : Invited Paper",
    "IEEE/ACM International Symposium on Nanoscale Architectures (NANOARCH)", "pp. 1-6, Nov. 2021",
    "10.1109/nanoarch53687.2021.9642252", "conference", ["Arias"], "HPC and hardware")
pub(2021, ["A. Ding", "Y. Li", "Q. Chen", "Y. Cao", "B. Liu", "S. Chen", "X. Liu"],
    "Gastric Location Classification During Esophagogastroduodenoscopy Using Deep Neural Networks",
    "IEEE 21st International Conference on Bioinformatics and Bioengineering (BIBE)", "pp. 1-8, Oct. 2021",
    "10.1109/bibe52308.2021.9635273", "conference", ["Cao"], "Digital health")
pub(2021, ["Z. Li", "J. Liu", "Y. Lin", "F. Wang"],
    "Grid-Constrained Data Cleansing Method for Enhanced Bus Load Forecasting",
    "IEEE Transactions on Instrumentation and Measurement", "vol. 70, art. no. 9002810, 2021",
    "10.1109/tim.2021.3075538", "journal", ["Lin"], "Smart grid")
pub(2021, ["C. J. Lin", "Y. Luo", "L. M. Wang"],
    "Heterogeneous Flow Scheduling using Deep Reinforcement Learning in Partially Observable NFV Environment",
    "International Conference on Networking and Network Applications (NaNA)", "pp. 432-436, Oct. 2021",
    "10.1109/nana53684.2021.00081", "conference", ["Luo"], "Sensing and networks")
pub(2021, ["Y. Lin", "A. Abur", "H. Xu"],
    "Identifying Security Vulnerabilities in Electricity Market Operations Induced by Weakly Detectable Network Parameter Errors",
    "IEEE Transactions on Industrial Informatics", "vol. 17, no. 1, pp. 627-636, Jan. 2021",
    "10.1109/tii.2020.3007424", "journal", ["Lin"], "Smart grid")
pub(2021, ["W. Wu", "P. Chen", "S. Wang", "V. Vardhanabhuti", "F. Liu", "H. Yu"],
    "Image-Domain Material Decomposition for Spectral CT Using a Generalized Dictionary Learning",
    "IEEE Transactions on Radiation and Plasma Medical Sciences", "vol. 5, no. 4, pp. 537-547, July 2021",
    "10.1109/trpms.2020.2997880", "journal", ["Yu"], "Medical imaging")
pub(2021, ["R. M. Osgood", "Y. Ait-El-Aoud", "S. Dinneen", "S. Giardini", "M. J. Yu", "J. H. Kim", "S. Johnson", "P. Moroshkin", "J. Xu", "G. Strack", "A. Akyurtlu", "L. Parameswaran", "C. Roberts", "M. Rothschild"],
    "Infrared-scattering sharply resonant nonlinear metasurfaces",
    "Metamaterials, Metadevices, and Metasystems 2021", "art. 30, Aug. 2021",
    "10.1117/12.2594572", "conference", ["Akyurtlu"], "Printed electronics")
pub(2021, ["C. Wang", "Y. Li", "Z. Xiong", "Y. Luo", "Y. Cao"],
    "Lower Body Rehabilitation Dataset and Model Optimization",
    "IEEE International Conference on Multimedia and Expo (ICME)", "pp. 1-6, July 2021",
    "10.1109/icme51207.2021.9428432", "conference", ["Luo", "Cao"], "Sensing and networks")
pub(2021, ["H. Zhang", "B. Liu", "H. Yu", "B. Dong"],
    "MetaInv-Net: Meta Inversion Network for Sparse View CT Image Reconstruction",
    "IEEE Transactions on Medical Imaging", "vol. 40, no. 2, pp. 621-634, Feb. 2021",
    "10.1109/tmi.2020.3033541", "journal", ["Yu"], "Medical imaging")
pub(2021, ["T. Griffin", "Y. Cao", "B. Liu", "M. J. Brunette", "X. Sun"],
    "Object Detection and Instance Segmentation in Chest X-rays for Tuberculosis Screening",
    "International Journal of Transdisciplinary Artificial Intelligence", "vol. 3, no. 1, pp. 1-24, Mar. 2021",
    "10.35708/tai1870-126250", "journal", ["Cao"], "Digital health")
pub(2021, ["K. Williams", "J. Foster", "A. Srivirote", "A. Hassan", "J. Tassarotti", "L. Tseng", "R. Palmieri"],
    "On Building Modular and Elastic Data Structures with Bulk Operations",
    "Proceedings of the 22nd International Conference on Distributed Computing and Networking", "pp. 237-238, Jan. 2021",
    "10.1145/3427796.3433932", "conference", ["Tseng"], "Distributed systems")
pub(2021, ["S. N. Edib", "Y. Lin", "V. M. Vokkarane", "F. Qiu", "R. Yao", "D. Zhao"],
    "Optimal PMU Restoration for Power System Observability Recovery After Massive Attacks",
    "IEEE Transactions on Smart Grid", "vol. 12, no. 2, pp. 1565-1576, Mar. 2021",
    "10.1109/tsg.2020.3028761", "journal", ["Vokkarane", "Lin"], "Optical networks")
pub(2021, ["T. Li", "L. Tseng", "T. Higuchi", "S. Ucar", "O. Altintas"],
    "Poster: Fault-tolerant Consensus for Connected Vehicles: A Case Study",
    "IEEE Vehicular Networking Conference (VNC)", "pp. 133-134, Nov. 2021",
    "10.1109/vnc52810.2021.9644680", "conference", ["Tseng"], "Distributed systems")
pub(2021, ["G. S. Gao", "K. Konwar", "J. Mantica", "H. Pan", "D. Russell Kish", "L. Tseng", "Z. Wang", "Y. Wu"],
    "Practical Experience Report: Cassandra+: Trading-Off Consistency, Latency, and Fault-tolerance in Cassandra",
    "Proceedings of the 22nd International Conference on Distributed Computing and Networking", "pp. 191-195, Jan. 2021",
    "10.1145/3427796.3427816", "conference", ["Tseng"], "Distributed systems")
pub(2021, ["Q. Zhang", "T. Bantikyan", "L. Tseng"],
    "Practical approximate consensus algorithms for small devices in lossy networks",
    "Proceedings of the 27th Annual International Conference on Mobile Computing and Networking", "pp. 840-842, Oct. 2021",
    "10.1145/3447993.3482865", "conference", ["Tseng"], "Distributed systems")
pub(2021, ["M. Inalpolat", "C. Traylor"],
    "Prediction of wind turbine blade trailing edge noise under various flow conditions for a passive damage detection system",
    "INTER-NOISE and NOISE-CON Congress and Conference Proceedings", "vol. 263, no. 2, pp. 4079-4087, Aug. 2021",
    "10.3397/in-2021-2597", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2021, ["N. Deane", "Y. Gu", "P. C. Kao", "Y. N. Wu", "M. Zielinski", "M. Inalpolat"],
    "Pressure monitoring based identification of the EOD suit\u2013human interface load distribution",
    "International Journal of Intelligent Robotics and Applications", "vol. 5, no. 3, pp. 410-423, May 2021",
    "10.1007/s41315-021-00178-z", "journal", ["Inalpolat"], "Structural dynamics and health monitoring")
pub(2021, ["X. Wen", "Y. Xie", "L. Wu", "L. Jiang"],
    "Quantifying and comparing the effects of key risk factors on various types of roadway segment crashes with LightGBM and SHAP",
    "Accident Analysis & Prevention", "vol. 159, art. 106261, Sept. 2021",
    "10.1016/j.aap.2021.106261", "journal", ["Xie"], "Transportation")
pub(2021, ["H. Pan", "J. Tuglu", "N. Zhou", "T. Wang", "Y. Shen", "X. Zheng", "J. Tassarotti", "L. Tseng", "R. Palmieri"],
    "Rabia",
    "Proceedings of the ACM SIGOPS 28th Symposium on Operating Systems Principles", "pp. 472-487, Oct. 2021",
    "10.1145/3477132.3483582", "conference", ["Tseng"], "Distributed systems")
pub(2021, ["M. DeFilippo", "M. Sacarny", "P. Robinette"],
    "RoboWhaler: A Robotic Vessel for Marine Autonomy and Dataset Collection",
    "OCEANS 2021: San Diego \u2013 Porto", "pp. 1-7, Sept. 2021",
    "10.23919/oceans44145.2021.9705871", "conference", ["Robinette"], "Robotics and human-robot interaction")
pub(2021, ["Z. Fang", "Y. Lin", "S. Song", "C. Li", "X. Lin", "Y. Chen"],
    "State Estimation for Situational Awareness of Active Distribution System With Photovoltaic Power Plants",
    "IEEE Transactions on Smart Grid", "vol. 12, no. 1, pp. 239-250, Jan. 2021",
    "10.1109/tsg.2020.3009571", "journal", ["Lin"], "Smart grid")
pub(2021, ["M. Southwick", "Z. Mao", "C. Niezrecki"],
    "Volumetric Motion Magnification: Subtle Motion Extraction from 4D Data",
    "Measurement", "vol. 176, art. 109211, May 2021",
    "10.1016/j.measurement.2021.109211", "journal", ["Niezrecki"], "Renewable energy and structural monitoring")
pub(2021, ["T. Griffin", "Q. Chen", "X. Sun", "D. Wang", "M. J. Brunette", "Y. Cao", "B. Liu"],
    "eRxNet: A Pipeline of Convolutional Neural Networks for Tuberculosis Screening",
    "Third International Conference on Transdisciplinary AI (TransAI)", "pp. 47-56, Sept. 2021",
    "10.1109/transai51903.2021.00017", "conference", ["Cao"], "Digital health")

# --- the publication list covers the director and center faculty only. Affiliated researchers
# and external collaborators keep their profile links; their own records live on their own pages.
CENTER_AUTHORS = {"Vokkarane"} | {re.sub(r"\(.*?\)", "", p["name"]).split()[-1] for p in FACULTY["core"]}
assert CENTER_AUTHORS == CORE, f"CORE at the top of this file is out of step with the roster: {CORE ^ CENTER_AUTHORS}"
P = [dict(p, faculty=[f for f in p["faculty"] if f in CENTER_AUTHORS]) for p in P if set(p["faculty"]) & CENTER_AUTHORS]

def _load_overlay(name, default):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    return json.load(open(p)) if os.path.exists(p) else default

# --- the founding years: papers from September 2019 through 2020, kept in their own file
for e in _load_overlay("pubs_2019_2020.json", {"entries": []}).get("entries", []):
    if e["doi"].lower() in {p["doi"].lower() for p in P if p.get("doi")}: continue
    P.append(dict(year=e["year"], authors=e["authors"], title=e["title"], venue=e["venue"], details=e["details"], doi=e["doi"],
                  type=e["type"], faculty=e["faculty"], area=e.get("area", ""), url=None))

# --- papers found in members' own CVs that the curated list lacked (Crossref-verified)
for e in _load_overlay("pubs_cv_additions.json", {"entries": []}).get("entries", []):
    if e["doi"].lower() in {p["doi"].lower() for p in P if p.get("doi")}: continue
    P.append(dict(year=e["year"], authors=e["authors"], title=e["title"], venue=e["venue"], details=e["details"], doi=e["doi"],
                  type=e["type"], faculty=e["faculty"], area=e.get("area", ""), url=None))

# --- Evans: credit his co-authored papers already in the record (the curated entries carry only engineering tags)
for _p in P:
    if any(re.sub(r"[.\s]", "", a).lower() in ("ngevans", "nevans") for a in _p["authors"]) and "Evans" not in _p["faculty"]:
        _p["faculty"] = list(_p["faculty"]) + ["Evans"]

# --- attribution: a paper counts for a member only from the year they joined UMass Lowell
JOIN_YEAR = {"Tseng": 2024, "Arias": 2021}
# Yuzhang Lin is an external center member at NYU. Only his papers with another center faculty member
# count as the center's; his independent work belongs to his own program.
NEEDS_CENTER_COAUTHOR = {"Lin", "Evans"}   # Lin is external; Evans publishes widely in ethics outside the center
def _attributed(p):
    fac = [f for f in p["faculty"] if p["year"] >= JOIN_YEAR.get(f, 0)]
    return [f for f in fac if f not in NEEDS_CENTER_COAUTHOR or len(fac) > 1]
P = [dict(p, faculty=_attributed(p)) for p in P if _attributed(p)]

# --- overlay: papers found by refresh.py since the curated list was written
_auto_pubs = _load_overlay("pubs_auto.json", {"entries": []})
_known = {p["doi"].lower() for p in P if p.get("doi")}
for e in _auto_pubs.get("entries", []):
    if e["doi"].lower() in _known or not set(e["faculty"]) & CENTER_AUTHORS: continue
    e = dict(e, faculty=[f for f in e["faculty"] if f in CENTER_AUTHORS])
    _fac = _attributed(e)          # join-year and co-author rules apply to found papers too
    if not _fac: continue
    P.append(dict(year=e["year"], authors=e["authors"], title=e["title"], venue=e["venue"], details=e["details"], doi=e["doi"],
                  type=e["type"], faculty=_fac, area=e.get("area", ""), url=None)); _known.add(e["doi"].lower())

MONTHS = {"Jan.":1,"Feb.":2,"Mar.":3,"Apr.":4,"May":5,"June":6,"July":7,"Aug.":8,"Sept.":9,"Oct.":10,"Nov.":11,"Dec.":12}
def month_of(p):
    for k, v in MONTHS.items():
        if re.search(r'\b' + re.escape(k) + r'(?=\s+\d{4})', p["details"]): return v
    return 0
P.sort(key=lambda p: (-p["year"], -month_of(p), 0 if p["type"] == "journal" else 1, p["title"].lower()))

NEWS = [
    ("Oct 2026", "SUMMIT begins. NSF's $2M Major Research Instrumentation Track 2 award funds a three-site federated smart grid testbed with NYU and West Virginia University, starting October 1, 2026; a postdoctoral search is under way."),
    ("Sep 2026", "The FUSION benchmarking framework paper appears in JOCN's special issue on benchmarking in optical networks, followed in October by a QoT-aware grooming paper for multi-band SDM networks."),
    ("Oct 2026", "ARPO-Sensor Fusion starts under the Massachusetts Technology Collaborative's Applied AI Models program ($625K, of which $247K to UMass Lowell and UMLARC), performed at UMLARC."),
    ("Aug 2026", "Lewis Tseng presents timely control for quantum clouds at the ACM SIGCOMM 2026 QuNet workshop."),
    ("Jun 2026", "Sukesh Aghara's group publishes in Energy Reports on phasing clean, sustainable alternatives into a university campus's central heating, and the Massachusetts nuclear roadmap enters its public discussion series with events in Boston, Worcester, and Lowell."),
    ("Mar 2026", "The U.S. Army ARPO project on autonomous robotic planning and optimization begins ($225K)."),
    ("Dec 2025", "Two GLOBECOM 2025 papers from the Tseng group: satellite-edge-enabled multi-drone search and content-aware gossip for mobile device clouds."),
    ("Sep 2025", "Two SmartGridComm 2025 papers: cyber-security-constrained economic dispatch, and smart false-data-injection attacks on smart meters with Orlando Arias and Yuzhang Lin; plus a joint ECOC 2025 paper on planning ultra-high-capacity multi-band SDM networks."),
    ("Oct 2025", "Gov. Maura Healey names Sukesh Aghara to lead the Massachusetts Advanced Nuclear and Fusion Energy Roadmaps, a statewide effort run from UMass Lowell."),
    ("Sep 2025", "Orlando Arias and Seung Woo Son publish on detecting silent data corruption from hardware counters at IEEE CLUSTER 2025."),
    ("Apr 2025", "Pineapple, which unifies Multi-Paxos and atomic shared registers, appears at USENIX NSDI 2025."),
]

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s, quote=True)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def fmt_authors(auths):
    out = []
    for a in auths:
        if not a.strip(): continue
        fam = a.split()[-1]
        if fam in CORE and (fam not in CORE_INITIAL or a.startswith(CORE_INITIAL[fam] + ".")):
            out.append(f'<b>{esc(a)}</b>')
        else:
            out.append(esc(a))
    return ", ".join(out)

def person_card(p, big=False):
    lines = [f'<h3>{esc(p["name"])}</h3>', f'<p class="ptitle">{esc(p["title"])}</p>', f'<p class="pareas">{esc(p["areas"])}</p>']
    if p.get("role"):
        lines.append(f'<p class="prole">{esc(p["role"])}</p>')
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(f'<span>{esc(p["phone"])}</span>')
    if p.get("office"): meta.append(f'<span>{esc(p["office"])}</span>')
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">{"NYU profile" if "nyu.edu" in p["url"] else ("LinkedIn" if "linkedin.com" in p["url"] else "UMass Lowell profile")}</a>')
    if p.get("inst", "Lowell") is not None: meta += id_links(p["name"])
    lines.append('<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in meta) + '</p>')
    if scholar_line(p["name"]): lines.append('<p class="gsline">' + scholar_line(p["name"]) + '</p>')
    lines.append(metrics_slot(p))
    return '<article class="person">' + "".join(lines) + '</article>'

def person_row(p):
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(esc(p["phone"]))
    return ('<li class="prow"><div><span class="pname">' + esc(p["name"]) + '</span> <span class="ptitle2">' + esc(p["title"]) + '</span>'
            '<span class="pareas2">' + esc(p["areas"]) + '</span></div><div class="pcontact">' + ' <span class="sep"></span> '.join(meta) + '</div></li>')

# ---------------------------------------------------------------- counts
n_pubs = len(P)
n_journal = sum(1 for p in P if p["type"] == "journal")
n_faculty = 1 + len(FACULTY["core"]) + len(FACULTY["affiliated"])
pub_json = json.dumps([{k: v for k, v in p.items()} for p in P], ensure_ascii=False)

# ---------------------------------------------------------------- images
# Photos are UMass Lowell's own (faculty headshots and site imagery from uml.edu), embedded as data URIs
# so the page is a single file. Regenerate images.json with prep_images.py if photos change.
import os
IMG = {}
_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images.json")
if os.path.exists(_img_path):
    IMG = json.load(open(_img_path))

def img_src(key):
    b64 = IMG.get(key)
    return f"data:image/jpeg;base64,{b64}" if b64 else ""

def avatar(p, size_cls):
    """Photo if we have one, otherwise a monogram."""
    key = p.get("photo")
    if key and IMG.get("head_" + key):
        return f'<img class="avatar {size_cls}" src="{img_src("head_" + key)}" alt="{esc(p["name"])}" width="420" height="420">'
    initials = "".join(w[0] for w in p["name"].replace("(", "").split() if w[0].isupper())[:2]
    return f'<span class="avatar mono {size_cls}" aria-hidden="true">{esc(initials)}</span>'

# ---------------------------------------------------------------- HTML
CSS = r"""
:root{
  --bg:#FFFFFF; --bg-2:#F3F5F8; --surface:#FFFFFF; --ink:#0E2036; --ink-2:#2B4162; --ink-3:#5B6B82;
  --line:#D5DCE5; --line-2:#E8EDF2; --signal:#0A777F; --signal-2:#08616A; --signal-tint:#E2F2F3;
  --amber:#3BA995; --amber-2:#DFF3EC; --amber-text:#1E6B5A; --green:#3BA995; --brand-blue:#044978;
  --navy:#0E2036; --navy-2:#09162A; --on-navy:#FFFFFF; --on-navy-2:#C9D3E0; --on-navy-3:#9AA9BC;
  --journal-bg:#DCEFF3; --journal-fg:#0B5A69; --shadow:rgba(14,32,54,.35); --nav-bg:rgba(255,255,255,.9);
  --grid-line:rgba(14,32,54,.07); --illus-bg:#EEF4F8; --illus-bg-2:#E2EDF4;
  --max:1180px; --gutter:clamp(18px,4vw,48px); --fs-0:clamp(15px,1.05vw,17px); --radius:12px;
}
:root[data-theme="dark"]{
  --bg:#0B1729; --bg-2:#0F1E33; --surface:#142640; --ink:#E8EEF5; --ink-2:#C2CDDB; --ink-3:#92A1B5;
  --line:#24384F; --line-2:#1B2D45; --signal:#3FC1D6; --signal-2:#5FD0E2; --signal-tint:#123645;
  --amber:#5FD0B6; --amber-2:#123A32; --amber-text:#9FE8D6; --green:#5FD0B6; --brand-blue:#7FB6E8;
  --navy:#08111F; --navy-2:#060C17; --journal-bg:#123645; --journal-fg:#7ADCEB; --shadow:rgba(0,0,0,.6);
  --nav-bg:rgba(11,23,41,.86); --grid-line:rgba(232,238,245,.06); --illus-bg:#0F2238; --illus-bg-2:#16304C;
  color-scheme:dark;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0B1729; --bg-2:#0F1E33; --surface:#142640; --ink:#E8EEF5; --ink-2:#C2CDDB; --ink-3:#92A1B5;
    --line:#24384F; --line-2:#1B2D45; --signal:#3FC1D6; --signal-2:#5FD0E2; --signal-tint:#123645;
    --amber:#5FD0B6; --amber-2:#123A32; --amber-text:#9FE8D6; --green:#5FD0B6; --brand-blue:#7FB6E8;
    --navy:#08111F; --navy-2:#060C17; --journal-bg:#123645; --journal-fg:#7ADCEB; --shadow:rgba(0,0,0,.6);
    --nav-bg:rgba(11,23,41,.86); --grid-line:rgba(232,238,245,.06); --illus-bg:#0F2238; --illus-bg-2:#16304C;
    color-scheme:dark;
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;overflow-x:hidden;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;font-size:var(--fs-0);line-height:1.55;-webkit-font-smoothing:antialiased;transition:background-color .25s ease,color .25s ease}
h1,h2,h3,h4{font-family:"Fraunces","Iowan Old Style",Georgia,serif;font-weight:600;letter-spacing:-.01em;margin:0;line-height:1.1;font-variation-settings:"opsz" 72,"SOFT" 30;color:var(--ink)}
h1{font-size:clamp(38px,5.2vw,66px);line-height:1.02;letter-spacing:-.02em;max-width:11em}
h2{font-size:clamp(30px,3.6vw,44px)}
h3{font-size:clamp(20px,1.7vw,24px)}
p{margin:0 0 1em}
a{color:var(--signal-2);text-decoration:none;text-underline-offset:.16em;text-decoration-thickness:1px}
a:hover{text-decoration:underline}
a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--amber);outline-offset:3px;border-radius:2px}
b{font-weight:600}
img{max-width:100%;height:auto}
.wrap{max-width:var(--max);margin:0 auto;padding:0 var(--gutter)}
a:focus-visible,button:focus-visible{outline:3px solid var(--signal);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-999px;top:8px;background:var(--navy);color:#fff;padding:8px 12px;z-index:100}
.skip:focus{left:8px}

/* nav */
.nav{position:sticky;top:0;z-index:50;background:var(--nav-bg);backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:66px;gap:12px}
.brand{display:flex;align-items:center;gap:10px;color:var(--ink);font-family:"Fraunces",Georgia,serif;font-size:19px;font-weight:600;letter-spacing:-.01em;flex:0 0 auto}
.brand>span{white-space:nowrap}
.brand small{display:block;font-family:"IBM Plex Sans",Arial,sans-serif;font-weight:400;font-size:12px;color:var(--ink-3);letter-spacing:0}
.brand .mark{display:inline-flex;align-items:center;justify-content:center;width:58px;height:40px;background:#fff;border-radius:8px;padding:3px;flex:none;border:1px solid transparent}
.brand .mark img{width:100%;height:100%;object-fit:contain;display:block}
:root[data-theme="dark"] .brand .mark{border-color:rgba(255,255,255,.25)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .brand .mark{border-color:rgba(255,255,255,.25)}}
.navright{display:flex;align-items:center;gap:6px;flex:0 0 auto}
.gift{display:inline-block;background:var(--green);color:#062B24;font-weight:600;font-size:13.5px;padding:8px 12px;border-radius:999px;white-space:nowrap}
.gift:hover{text-decoration:none;filter:brightness(1.06)}
.links{display:flex;gap:0;list-style:none;margin:0;padding:0}
.links a{display:block;padding:8px 9px;color:var(--ink-2);font-size:14px;border-radius:6px;white-space:nowrap}
.links a:hover{background:var(--line-2);text-decoration:none;color:var(--ink)}
.links a[aria-current="true"]{color:var(--ink);box-shadow:inset 0 -2px 0 var(--signal)}
.navtoggle{display:none;background:none;border:1px solid var(--line);border-radius:6px;padding:7px 10px;font:inherit;color:var(--ink)}
.theme{display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 10px 6px 8px;font:inherit;font-size:13.5px;color:var(--ink-2);cursor:pointer}
.theme:hover{border-color:var(--ink-3)}
.theme svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.theme .sun{display:none}
:root[data-theme="dark"] .theme .sun{display:block}
:root[data-theme="dark"] .theme .moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .theme .sun{display:block}:root:not([data-theme="light"]) .theme .moon{display:none}}
@media (max-width:1600px){.brand small{display:none}}
@media (max-width:1240px){.theme .lbl{display:none}.theme{padding:7px 8px}}
@media (max-width:1100px){
  .links{display:none;position:absolute;left:0;right:0;top:66px;background:var(--bg);border-bottom:1px solid var(--line);flex-direction:column;padding:8px var(--gutter) 14px}
  .links a{font-size:15px;padding:10px 12px}
  .links.open{display:flex}
  .navtoggle{display:inline-block}
}

/* hero with photo */
.hero{position:relative;color:#fff;min-height:min(78vh,720px);display:flex;align-items:center;isolation:isolate;overflow:hidden;background:var(--navy)}
.hero .bg{position:absolute;inset:0;z-index:-2;background-size:cover;background-position:62% 50%}
.hero .veil{position:absolute;inset:0;z-index:-1;background:linear-gradient(100deg,rgba(9,22,40,.94) 0%,rgba(9,22,40,.86) 38%,rgba(9,22,40,.45) 70%,rgba(9,22,40,.25) 100%)}
:root[data-theme="dark"] .hero .veil{background:linear-gradient(100deg,rgba(6,12,23,.96) 0%,rgba(6,12,23,.88) 38%,rgba(6,12,23,.55) 70%,rgba(6,12,23,.35) 100%)}
@media (max-width:860px){.hero .veil{background:linear-gradient(180deg,rgba(9,22,40,.9) 0%,rgba(9,22,40,.82) 60%,rgba(9,22,40,.55) 100%)}}
.hero .wrap{padding-top:clamp(64px,9vw,120px);padding-bottom:clamp(96px,11vw,150px);width:100%}
.hero-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:clamp(24px,5vw,64px);align-items:center}
.hero-logo{background:#fff;border-radius:16px;padding:clamp(18px,2.4vw,30px);box-shadow:0 30px 70px -30px rgba(0,0,0,.6);max-width:420px;justify-self:end}
.hero-logo img{width:100%;height:auto;display:block}
@media (max-width:900px){.hero-grid{grid-template-columns:1fr}.hero-logo{justify-self:start;max-width:320px}}
.hero h1{color:#fff}
.hero p.lede{font-size:clamp(17px,1.45vw,20.5px);line-height:1.5;color:#D6DEE8;max-width:33em;margin:26px 0 32px}
.cta{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-block;padding:13px 20px;border-radius:8px;font-weight:500;font-size:15px;border:1px solid rgba(255,255,255,.6);color:#fff;background:transparent}
.btn.primary{background:#fff;color:#0E2036;border-color:#fff}
.btn:hover{text-decoration:none;background:var(--signal);border-color:var(--signal);color:#fff}

/* facts card overlapping hero */
.factsbar{position:relative;z-index:2;margin-top:-64px}
.facts{display:grid;grid-template-columns:repeat(4,1fr);background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 18px 50px -24px var(--shadow);overflow:hidden}
.facts div{padding:26px 24px;border-right:1px solid var(--line)}
.facts div:last-child{border-right:0}
.facts strong{display:block;font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:clamp(28px,2.8vw,38px);line-height:1;letter-spacing:-.02em;margin-bottom:8px;color:var(--ink)}
.facts span{font-size:14px;color:var(--ink-3);line-height:1.4;display:block}
@media (max-width:760px){.factsbar{margin-top:-40px}.facts{grid-template-columns:1fr 1fr}.facts div:nth-child(2){border-right:0}.facts div:nth-child(n+3){border-top:1px solid var(--line)}}

/* sections */
section{padding:clamp(60px,7vw,104px) 0}
section.tint{background:var(--bg-2)}
.shead{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:20px clamp(24px,5vw,72px);align-items:end;margin-bottom:clamp(30px,4vw,52px)}
.shead h2{position:relative;padding-top:18px}
.shead h2::before{content:"";position:absolute;left:0;top:0;width:52px;height:3px;background:linear-gradient(90deg,var(--brand-blue),var(--green));border-radius:2px}
.shead p{color:var(--ink-2);font-size:clamp(16px,1.25vw,18.5px);max-width:38em;margin:0}
@media (max-width:760px){.shead{grid-template-columns:1fr}}

/* about */
.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:clamp(32px,4vw,52px)}
.gallery figure{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:0 18px 50px -34px var(--shadow)}
.gallery img{width:100%;aspect-ratio:3/2;object-fit:cover;display:block}
.gallery figcaption{padding:12px 16px 14px;font-size:13.5px;line-height:1.45;color:var(--ink-2)}
@media (max-width:860px){.gallery{grid-template-columns:1fr}}
.about-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(24px,5vw,72px);align-items:start}
.about-grid p{max-width:38em}
.goals{list-style:none;margin:12px 0 0;padding:0;border-top:1px solid var(--line)}
.goals li{padding:16px 0;border-bottom:1px solid var(--line)}
.goals h4{font-size:17px;margin-bottom:6px}
.goals p{margin:0;color:var(--ink-2);font-size:15px}
.domains{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.domains span{border:1px solid var(--line);background:var(--bg-2);border-radius:999px;padding:6px 14px;font-size:14px}
@media (max-width:760px){.about-grid{grid-template-columns:1fr}}
.loop{margin-top:clamp(40px,5vw,64px);display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,.6fr);gap:clamp(20px,4vw,56px);align-items:center}
.schem{margin:0;border:1px solid var(--line);border-radius:var(--radius);color:var(--ink);background:linear-gradient(180deg,var(--surface),var(--bg-2));padding:22px 18px 14px;box-shadow:0 12px 40px -28px var(--shadow)}
.schem svg{width:100%;height:auto;display:block}
.schem .s-ink{stroke:var(--ink)} .schem .f-ink{fill:var(--ink)} .schem .f-surface{fill:var(--surface)} .schem .f-muted{fill:var(--ink-3)} .schem .f-ink2{fill:var(--ink-2)}
.schem .s-sig{stroke:var(--signal)} .schem .f-sig{fill:var(--signal)} .schem .f-amb{fill:var(--amber)} .schem .s-amb{stroke:var(--amber)}
.schem .f-brand{fill:var(--brand-blue)} .schem .s-brand{stroke:var(--brand-blue)} .schem .f-grn{fill:var(--green)} .schem .s-grn{stroke:var(--green)} .schem .f-tint{fill:var(--bg-2)} .schem .s-line{stroke:var(--line)} .schem .f-line{fill:var(--line)}
.schem .card{filter:drop-shadow(0 6px 14px rgba(4,73,120,.12))}
:root[data-theme="dark"] .schem .card{filter:drop-shadow(0 6px 14px rgba(0,0,0,.45))}
.loop .txt h3{margin-bottom:10px}
.loop .txt p{color:var(--ink-2);font-size:15.5px}
@media (max-width:900px){.loop{grid-template-columns:1fr}}
.flow{stroke-dasharray:3 9;animation:flow 2.6s linear infinite}
.offscreen .flow,.offscreen .pulse,.offscreen .spin,.offscreen .grow,.offscreen .trace,.offscreen .fed-flow{animation-play-state:paused}
.flow.slow{animation-duration:4.2s}
@keyframes flow{to{stroke-dashoffset:-48}}
.pulse{animation:pulse 3s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
.spin{animation:spin 7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.grow{animation:grow 3.2s ease-in-out infinite}
@keyframes grow{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.72)}}
.trace{stroke-dasharray:60 100;animation:trace 3s linear infinite}
@keyframes trace{from{stroke-dashoffset:60}to{stroke-dashoffset:-100}}
@media (prefers-reduced-motion:reduce){.flow,.pulse,.spin,.grow,.trace{animation:none}.flow{stroke-dasharray:none}.trace{stroke-dasharray:none}}

/* research */
.thrusts{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.thrust{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
.thrust .art{display:block;aspect-ratio:2/1;background:#FFFFFF;--bg-2:#F3F7FA;--surface:#FFFFFF;--line:#D5DCE5;--ink:#0E2036;--ink-3:#5B6B82;--signal:#0A777F;--brand-blue:#044978;--green:#3BA995;background:linear-gradient(160deg,var(--illus-bg),var(--illus-bg-2));color:var(--ink);border-bottom:1px solid var(--line);padding:6px}
.thrust .art svg{width:100%;height:100%;display:block}
.thrust .art .s-ink{stroke:var(--ink)} .thrust .art .f-ink{fill:var(--ink)} .thrust .art .f-surface{fill:var(--surface)} .thrust .art .f-muted{fill:var(--ink-3)}
.thrust .art .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}
:root[data-theme="dark"] .thrust .art .card{filter:drop-shadow(0 4px 10px rgba(0,0,0,.4))}
.thrust .art .f-alert{fill:#E25555} .thrust .art .s-alert{stroke:#E25555} .thrust .art .f-alert-tint{fill:#FDECEC}
:root[data-theme="dark"] .thrust .art .f-alert-tint{fill:#3A1E20}
.thrust .art .s-sig{stroke:var(--signal)} .thrust .art .f-sig{fill:var(--signal)} .thrust .art .f-brand{fill:var(--brand-blue)} .thrust .art .s-brand{stroke:var(--brand-blue)} .thrust .art .f-grn{fill:var(--green)} .thrust .art .s-grn{stroke:var(--green)} .thrust .art .f-tint{fill:var(--bg-2)} .thrust .art .s-line{stroke:var(--line)} .thrust .art .f-line{fill:var(--line)} .thrust .art .f-sigt{fill:var(--signal-tint)} .thrust .art .f-amb{fill:var(--amber)} .thrust .art .s-amb{stroke:var(--amber)} .thrust .art .s-muted{stroke:var(--ink-3)}
.thrust .body{padding:22px 24px 24px;display:flex;flex-direction:column;flex:1}
.thrust h3{font-size:20px;margin-bottom:8px}
.thrust h3 a{color:var(--ink)}
.thrust h3 a:hover{color:var(--signal-2)}
.thrust .more2{margin:12px 0 0;font-size:14px;font-weight:500}
.thrust .more2 a{color:var(--signal-2)}
.thrust .more2 a::after{content:" \2192"}
.thrust p{color:var(--ink-2);font-size:15px;margin:0 0 12px}
.thrust .who{font-size:13.5px;color:var(--ink-3);border-top:1px solid var(--line-2);padding-top:10px;margin-top:auto}
@media (max-width:980px){.thrusts{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.thrusts{grid-template-columns:1fr}}

/* SUMMIT feature */
.feature{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);background:var(--navy);color:#fff;border-radius:var(--radius);overflow:hidden;margin-bottom:clamp(36px,5vw,56px);isolation:isolate;border:1px solid var(--line)}
.feature .copy{padding:clamp(28px,4vw,52px)}
.feature .kicker{display:inline-block;background:#3BA995;color:#062B24;font-weight:500;font-size:13px;padding:4px 10px;border-radius:5px;margin-bottom:18px}
.feature h3{font-size:clamp(24px,2.4vw,32px);color:#fff;margin-bottom:12px}
.feature p{color:var(--on-navy-2);max-width:36em}
.feature .meta{display:grid;grid-template-columns:1fr 1fr;gap:14px 24px;margin-top:22px;padding-top:18px;border-top:1px solid rgba(255,255,255,.15)}
.feature .meta b{display:block;color:#fff;font-weight:600;font-size:15px}
.feature .meta span{font-size:13.5px;color:var(--on-navy-3)}
.meta a{color:#9FDCD6;text-decoration:underline;text-decoration-color:rgba(159,220,214,.5)}
.meta a:hover{color:#fff}
.feature .paradigms{padding:clamp(28px,4vw,52px) clamp(24px,3vw,40px) clamp(28px,4vw,52px) 0;border-left:1px solid rgba(255,255,255,.15);padding-left:clamp(24px,3vw,40px)}
.feature .paradigms h4{color:#fff;font-size:18px;margin-bottom:12px}
.feature .paradigms ol{margin:0 0 14px;padding-left:20px;color:var(--on-navy-2);font-size:14.5px;line-height:1.5}
.feature .paradigms li{margin-bottom:9px}
.feature .paradigms li b{color:#fff;font-weight:600}
.feature .paradigms .scope{font-size:13.5px;color:var(--on-navy-3);margin:0}
.feature .paradigms .more{margin:18px 0 0}
.summit-btn{display:inline-block;width:auto;max-width:none;text-align:left;background:#3BA995;color:#062B24;padding:11px 18px;font-size:14.5px;border-radius:8px}
.more{margin:22px 0 0}
.more .summit-btn{background:var(--ink);color:#fff}
.feature .arch{grid-column:1 / -1;margin:0;background:#fff;padding:18px 22px 14px;border-top:1px solid rgba(255,255,255,.15)}
.feature .arch img{width:100%;height:auto;display:block}
.feature .arch figcaption{font-size:13px;color:#5B6B82;text-align:center;margin-top:10px}
@media (max-width:860px){.feature .paradigms{border-left:0;border-top:1px solid rgba(255,255,255,.15);padding-left:clamp(24px,4vw,52px)}}
@media (max-width:860px){.feature{grid-template-columns:1fr}}
.fed-flow{stroke-dasharray:2 8;animation:flow 3.4s linear infinite}
@media (prefers-reduced-motion:reduce){.fed-flow{animation:none;stroke-dasharray:none}}

/* projects ledger */
.ledger{border-top:2px solid var(--ink)}
.proj{display:grid;grid-template-columns:150px minmax(0,1fr) 210px;gap:12px 28px;padding:24px 0;border-bottom:1px solid var(--line)}
.proj .when{font-size:14px;color:var(--ink-2);line-height:1.4}
.proj .when .tag{display:inline-block;font-size:12.5px;font-weight:500;padding:3px 9px;border-radius:4px;background:var(--line-2);color:var(--ink-2);margin-bottom:10px}
.proj .when .tag.new{background:var(--amber-2);color:var(--amber-text)}
.proj h3{font-size:19px;margin-bottom:6px}
.proj .sponsor{font-size:14.5px;color:var(--ink-3);margin-bottom:8px}
.proj .role{display:inline-block;background:var(--signal-tint);color:var(--signal-2);font-size:11.5px;font-weight:600;padding:2px 8px;border-radius:999px;margin-right:9px;vertical-align:1px}
.proj .desc{margin:0 0 8px;color:var(--ink-2);max-width:60em}
.proj .team{font-size:14px;color:var(--ink-3);margin:0}
.proj .amt{text-align:right;font-family:"Fraunces",Georgia,serif;font-size:22px;font-weight:600;letter-spacing:-.01em;line-height:1.15}
.proj .amt small{display:block;font-family:"IBM Plex Sans",Arial,sans-serif;font-weight:400;font-size:13px;color:var(--ink-3);margin-top:6px;letter-spacing:0}
@media (max-width:860px){.proj{grid-template-columns:1fr}.proj .amt{text-align:left}}
.tools{margin-top:52px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.tool{display:flex;flex-direction:column;background:var(--bg-2);border-radius:var(--radius);padding:22px 22px 24px;border:1px solid var(--line)}
.tool h4{font-size:17px;margin-bottom:6px}
.toolfig{width:100%;aspect-ratio:64/30;background:#FFFFFF;border-radius:8px;border:1px solid var(--line);margin-bottom:14px;overflow:hidden;display:flex;align-items:center;
  --bg-2:#F3F7FA;--surface:#FFFFFF;--line:#D5DCE5;--ink:#0E2036;--ink-3:#5B6B82;--signal:#0A777F;--brand-blue:#044978;--green:#3BA995}
.toolfig svg,.toolfig img{width:100%;height:100%;object-fit:contain;display:block}
.tool p{flex:1}
.tool .toollink{margin-top:14px;flex:none}
.toolfig .s-ink{stroke:var(--ink)}
.toolfig .f-ink{fill:var(--ink)}
.toolfig .f-surface{fill:var(--surface)}
.toolfig .f-muted{fill:var(--ink-3)}
.toolfig .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}

.toolfig .f-alert{fill:#E25555}
.toolfig .s-alert{stroke:#E25555}
.toolfig .f-alert-tint{fill:#FDECEC}

.toolfig .s-sig{stroke:var(--signal)}
.toolfig .f-sig{fill:var(--signal)}
.toolfig .f-brand{fill:var(--brand-blue)}
.toolfig .s-brand{stroke:var(--brand-blue)}
.toolfig .f-grn{fill:var(--green)}
.toolfig .s-grn{stroke:var(--green)}
.toolfig .f-tint{fill:var(--bg-2)}
.toolfig .s-line{stroke:var(--line)}
.toolfig .f-line{fill:var(--line)}
.toolfig .f-sigt{fill:var(--signal-tint)}
.toolfig .f-amb{fill:var(--amber)}
.toolfig .s-amb{stroke:var(--amber)}
.toolfig .s-muted{stroke:var(--ink-3)}
.tool p{font-size:14.5px;color:var(--ink-2);margin:0}
.tool .toollink{margin-top:10px;font-weight:500}
@media (max-width:760px){.tools{grid-template-columns:1fr}}

/* people */
.avatar{border-radius:14px;object-fit:cover;display:block;background:var(--line-2);flex:none}
.avatar.xl{width:min(100%,300px);aspect-ratio:1/1;border-radius:18px}
.avatar.lg{width:112px;height:112px}
.avatar.sm{width:150px;height:150px;border-radius:14px}
.avatar.mono{display:grid;place-items:center;font-family:"Fraunces",Georgia,serif;font-weight:600;color:var(--ink-2);background:var(--signal-tint)}
.avatar.mono.sm{font-size:20px}
.director{display:grid;grid-template-columns:300px minmax(0,1fr);gap:clamp(24px,4vw,56px);padding:34px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);align-items:start}
.director .bio{color:var(--ink-2);max-width:48em;margin-top:14px}
.director .bio p{margin:0}
.person h3{margin-bottom:4px}
.ptitle{color:var(--ink-2);font-size:14.5px;margin-bottom:8px}
.ptitle.strong{color:var(--ink);font-weight:700;font-size:16px;margin:-4px 0 10px}
.pareas{font-size:15px;margin-bottom:8px}
.prole{font-size:14.5px;color:var(--ink-2);margin-bottom:8px}
.pmeta{font-size:13.5px;color:var(--ink-3);margin:0;display:flex;flex-wrap:wrap;gap:4px 0}
.pmeta .mi{white-space:nowrap}
.pmeta .mi a[href^="mailto"]{overflow-wrap:anywhere;white-space:normal}
.pmeta{gap:4px 14px}
.pmeta .mi::after{content:""}
.metrics{display:none}
.metrics:empty{display:none}
.metrics b{color:var(--ink);font-weight:600}
.metrics .src{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:1px 6px;letter-spacing:.02em}
@media (max-width:760px){.director{grid-template-columns:1fr;padding:22px}}
.core{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-top:18px}
.core .person{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px}
.core .avatar{margin-bottom:16px}
.core .avatar.lg{width:220px;height:220px;border-radius:16px}
@media (max-width:860px){.core{grid-template-columns:1fr}}
.group{margin-top:48px}
.grouph{font-family:"Fraunces",Georgia,serif;font-size:22px;margin:0 0 14px}
.founding{font-size:14px;color:var(--ink-3);margin:-8px 0 26px}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.group .grouph{font-family:"Fraunces",Georgia,serif;font-size:22px;margin-bottom:6px}
.group>p{color:var(--ink-3);font-size:14.5px;margin-bottom:14px}
.plist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.prow{display:flex;gap:16px;padding:16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);align-items:flex-start}
.prow>div{min-width:0;flex:1 1 auto}
.pname{font-weight:600;display:block}
.ptag{display:inline-block;margin-left:8px;vertical-align:3px;font-family:"IBM Plex Sans",Arial,sans-serif;letter-spacing:0;font-size:11.5px;font-weight:500;padding:2px 8px;border-radius:999px;background:var(--signal-tint);color:var(--signal-2)}
.ptitle2{color:var(--ink-2);font-size:14px;display:block}
.pareas2{display:block;font-size:13.5px;color:var(--ink-3);margin-top:3px}
.pnote{display:block;font-size:13.5px;color:var(--ink-2);margin-top:7px}
.pcontact{font-size:13px;color:var(--ink-3);margin-top:6px;display:flex;flex-wrap:wrap;gap:3px 14px}
.pcontact .ci{white-space:nowrap}
.pcontact .ci a{overflow-wrap:anywhere;white-space:normal}
@media (max-width:860px){.plist{grid-template-columns:1fr}}
@media (max-width:520px){.avatar.sm{width:110px;height:110px}}
.partners{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;list-style:none;margin:0;padding:0}
.partners li{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;font-size:14.5px}
.partners b{display:block;font-weight:600;margin-bottom:2px}
.partners span{display:block;color:var(--ink-3);font-size:13.5px}
@media (max-width:760px){.partners{grid-template-columns:1fr}}

/* sponsors */
.sgroup{margin-bottom:34px}
.sgroup h3{font-size:20px;margin-bottom:12px}
.logos{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.logo-tile{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;min-height:168px;padding:22px 20px;background:#FFFFFF;border:1px solid var(--line);border-radius:var(--radius);color:#0E2036;text-decoration:none;transition:box-shadow .2s ease,transform .2s ease}
a.logo-tile:hover{text-decoration:none;box-shadow:0 14px 34px -22px var(--shadow);transform:translateY(-2px)}
.logo-tile .mark{display:flex;align-items:center;justify-content:center;min-height:92px;width:100%}
.logo-tile img{max-height:88px;max-width:82%;width:auto;object-fit:contain}
.logo-tile .wm{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:19px;line-height:1.2;letter-spacing:-.01em;color:#0E2036;max-width:14em}
.logo-tile .note{font-size:12.5px;color:#5B6B82;margin-top:12px;line-height:1.4;max-width:22em}
@media (max-width:980px){.logos{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){.logos{grid-template-columns:1fr}}
.ack{margin-top:10px;padding:22px 24px;border-left:3px solid var(--signal);background:var(--bg-2);border-radius:0 var(--radius) var(--radius) 0;font-size:14.5px;color:var(--ink-2);max-width:70em}
.ack p{margin:0 0 8px}
.ack p:last-child{margin:0}

/* organization diagram */
.orgh{margin:clamp(36px,5vw,56px) 0 16px;font-size:24px}
.orgfig{margin:0;background:#FFFFFF;border:1px solid var(--line);border-radius:var(--radius);padding:14px;
  --bg-2:#F3F7FA;--surface:#FFFFFF;--line:#D5DCE5;--ink:#0E2036;--ink-3:#5B6B82;--signal:#0A777F;--brand-blue:#044978;--green:#3BA995}
.orgfig svg{width:100%;height:auto;display:block}
.orgnote{font-size:15px;color:var(--ink-2);margin:16px auto 0;max-width:62em;text-align:center}
.orgfig .s-ink{stroke:var(--ink)}
.orgfig .f-ink{fill:var(--ink)}
.orgfig .f-surface{fill:var(--surface)}
.orgfig .f-muted{fill:var(--ink-3)}
.orgfig .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}

.orgfig .f-alert{fill:#E25555}
.orgfig .s-alert{stroke:#E25555}
.orgfig .f-alert-tint{fill:#FDECEC}

.orgfig .s-sig{stroke:var(--signal)}
.orgfig .f-sig{fill:var(--signal)}
.orgfig .f-brand{fill:var(--brand-blue)}
.orgfig .s-brand{stroke:var(--brand-blue)}
.orgfig .f-grn{fill:var(--green)}
.orgfig .s-grn{stroke:var(--green)}
.orgfig .f-tint{fill:var(--bg-2)}
.orgfig .s-line{stroke:var(--line)}
.orgfig .f-line{fill:var(--line)}
.orgfig .f-sigt{fill:var(--signal-tint)}
.orgfig .f-amb{fill:var(--amber)}
.orgfig .s-amb{stroke:var(--amber)}
.orgfig .s-muted{stroke:var(--ink-3)}

/* mission hub */
.hubwrap{margin-bottom:clamp(36px,5vw,56px)}
.hubfig{margin:0;background:#FFFFFF;border:1px solid var(--line);border-radius:var(--radius);padding:10px;--bg-2:#F3F7FA;--surface:#FFFFFF;--line:#D5DCE5;--ink:#0E2036;--ink-3:#5B6B82;--signal:#0A777F;--brand-blue:#044978;--green:#3BA995}
.hubfig svg{width:100%;height:auto;display:block;max-height:none}
.hublist{margin-top:26px}
.hublist h3{font-size:22px;margin-bottom:14px;text-align:center}
.hublist ol{margin:0 auto;padding-left:24px;max-width:70em;columns:2;column-gap:clamp(28px,5vw,64px)}
.hublist li{font-size:15.5px;color:var(--ink-2);margin-bottom:12px;padding-left:4px;break-inside:avoid}
.hublist li::marker{color:var(--signal-2);font-weight:600}
@media (max-width:760px){.hublist ol{columns:1}}
.hubfig .s-ink{stroke:var(--ink)}
.hubfig .f-ink{fill:var(--ink)}
.hubfig .f-surface{fill:var(--surface)}
.hubfig .f-muted{fill:var(--ink-3)}
.hubfig .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}

.hubfig .f-alert{fill:#E25555}
.hubfig .s-alert{stroke:#E25555}
.hubfig .f-alert-tint{fill:#FDECEC}

.hubfig .s-sig{stroke:var(--signal)}
.hubfig .f-sig{fill:var(--signal)}
.hubfig .f-brand{fill:var(--brand-blue)}
.hubfig .s-brand{stroke:var(--brand-blue)}
.hubfig .f-grn{fill:var(--green)}
.hubfig .s-grn{stroke:var(--green)}
.hubfig .f-tint{fill:var(--bg-2)}
.hubfig .s-line{stroke:var(--line)}
.hubfig .f-line{fill:var(--line)}
.hubfig .f-sigt{fill:var(--signal-tint)}
.hubfig .f-amb{fill:var(--amber)}
.hubfig .s-amb{stroke:var(--amber)}
.hubfig .s-muted{stroke:var(--ink-3)}

/* project filters */
.pfilters{display:grid;gap:10px;margin:0 0 6px}
.frow{display:grid;grid-template-columns:84px auto minmax(0,1fr);gap:8px;align-items:start}
.frow .flab{font-size:13px;color:var(--ink-3);padding-top:7px}
.fchips{display:flex;flex-wrap:wrap;gap:8px}
.pfilters .chip{font:inherit;font-size:13.5px;padding:5px 12px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);border-radius:999px;cursor:pointer}
.pfilters .chip[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
.pfilters .chip:disabled{opacity:.45;cursor:default}
.pcount{font-size:13.5px;color:var(--ink-3);margin:14px 0 2px}
.proj[hidden]{display:none}
@media (max-width:640px){.frow{grid-template-columns:auto minmax(0,1fr)}.frow .flab{grid-column:1/-1;padding-top:0}}

/* teasers, news page, article stream */
.peoplecards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.pcard{display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:26px 24px;color:var(--ink);transition:box-shadow .2s ease,transform .2s ease}
.pcard:hover{text-decoration:none;box-shadow:0 16px 40px -26px var(--shadow);transform:translateY(-2px)}
.pcard .pnum{font-family:"Fraunces",Georgia,serif;font-size:42px;font-weight:600;line-height:1;letter-spacing:-.02em}
.pcard .plab{font-weight:600;margin:6px 0 10px}
.pcard .pdesc{font-size:14.5px;color:var(--ink-2);flex:1}
.pcard .pgo{margin-top:16px;font-size:14px;font-weight:500;color:var(--signal-2)}
.pcard .pgo::after{content:" \2192"}
@media (max-width:820px){.peoplecards{grid-template-columns:1fr}}

.publist.teaser{margin-bottom:22px}
.newsgrid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,.9fr);gap:clamp(28px,4vw,56px);align-items:start}
.nitem{display:grid;grid-template-columns:104px 1fr;gap:20px;padding:20px 0;border-top:1px solid var(--line)}
.nitem:first-child{border-top:2px solid var(--ink)}
.nitem .nwhen{color:var(--ink-3);font-size:13.5px;padding-top:3px;line-height:1.35}
.nitem .nkind{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.03em;text-transform:uppercase;padding:2px 8px;border-radius:999px;background:var(--signal-tint);color:var(--signal-2);margin-bottom:7px}
.nitem .nkind.award{background:var(--amber-2);color:var(--amber-text)}
.nitem .nkind.milestone{background:var(--journal-bg);color:var(--journal-fg)}
.nitem .nkind.journal{background:var(--journal-bg);color:var(--journal-fg)}
.nitem .nkind.conf{background:var(--bg-2);color:var(--ink-2)}
.nitem .nkind.chapter{background:var(--amber-2);color:var(--amber-text)}
.nitem .nkind.talk{background:var(--signal-tint);color:var(--signal-2)}
.nitem[hidden]{display:none}
.nfilters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:2px}
.nfilters .lab{font-size:13px;color:var(--ink-3);margin-right:4px}
.nfilters .chip{font:inherit;font-size:13.5px;padding:6px 13px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);border-radius:999px;cursor:pointer}
.nfilters .chip[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
.nfilters .chip:disabled{opacity:.4;cursor:default}
.ncount{font-size:13.5px;color:var(--ink-3);margin:14px 0 2px}
.nitem h3{font-size:19px;margin-bottom:5px;line-height:1.3}
.nitem p{font-size:15px;color:var(--ink-2);margin:0}
.nitem .nlink{font-size:14px;margin-top:7px}
.stream{position:sticky;top:86px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px 20px 8px}
.stream .grouph{font-size:17px;margin-bottom:2px}
.stream .sub{font-size:13px;color:var(--ink-3);margin-bottom:12px}
.stream ol{list-style:none;margin:0;padding:0;max-height:70vh;overflow-y:auto}
.stream li{padding:12px 0;border-top:1px solid var(--line-2)}
.stream li:first-child{border-top:0}
.stream .t{font-size:14px;font-weight:600;line-height:1.35;display:block}
.stream .v{font-size:12.5px;color:var(--ink-3);display:block;margin-top:3px}
.stream .k{font-size:10.5px;font-weight:600;letter-spacing:.03em;text-transform:uppercase;color:var(--signal-2)}
.stream .foot{border-top:1px solid var(--line);padding:12px 0 10px;font-size:13px}
@media (max-width:900px){.newsgrid{grid-template-columns:1fr}.stream{position:static}.stream ol{max-height:none}}
@media (max-width:640px){.nitem{grid-template-columns:1fr;gap:4px}}

/* DOI and journal metrics */
.pub .doi{font-size:12.5px;color:var(--ink-3);margin-top:3px;font-variant-numeric:tabular-nums}
.pub .doi a{color:var(--ink-3);text-decoration:underline dotted}
.pub .doi a:hover{color:var(--signal-2)}
.jm{display:inline-block;margin-left:10px;font-size:11.5px;font-weight:600;letter-spacing:.01em;padding:1px 8px;border-radius:999px;background:var(--journal-bg);color:var(--journal-fg);vertical-align:1px;white-space:nowrap}

.ico{width:1em;height:1em;vertical-align:-.15em;display:inline-block}
/* capstone sponsorship */
.capbox{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--signal);border-radius:var(--radius);padding:22px 24px}
.capbox h3{margin:0 0 10px;font-size:20px}
.capbox p{font-size:15px;line-height:1.55;margin:0 0 12px}
.capcta{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-top:16px!important}
.capmail{font-size:15px;font-weight:600}
.capfine{font-size:13px;color:var(--ink-3);margin-top:8px!important}
/* alumni profiles */
.alnote{font-size:14px;color:var(--ink-3);margin:-6px 0 18px;max-width:60em}
.alumgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:18px;margin-bottom:38px}
.alum{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px}
.alumhead{display:flex;gap:16px;align-items:flex-start;margin-bottom:10px}
.alumpic{width:80px;height:80px;border-radius:50%;object-fit:cover;flex:none;background:var(--bg-2)}
.alumpic.mono{display:flex;align-items:center;justify-content:center;font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:22px;color:var(--brand-blue)}
.alum h3{font-size:18px;margin:2px 0 4px}
.aldeg{font-size:13.5px;color:var(--ink-3);margin:0 0 4px}.alinst{color:var(--ink-2)}
.alrole{font-size:14.5px;margin:0}.alrole b{color:var(--ink)}
.alpath{font-size:13.5px;color:var(--ink-3);margin:0 0 6px}
.alfocus{font-size:14px;line-height:1.5;margin:0 0 10px}
.alum .pmeta{margin:0 0 6px}.alum .gsline{font-size:13px;color:var(--ink-3);margin:0}
/* students and alumni */
.stugrid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.stugrid.two{grid-template-columns:repeat(2,1fr);margin-bottom:40px}
.advgroup{margin:0 0 34px}.advh{font-size:20px;margin:0 0 14px;display:flex;align-items:baseline;gap:10px}.advh .advn{font-size:13px;font-weight:600;color:var(--ink-3);border:1px solid var(--line);border-radius:999px;padding:1px 9px}
.stulist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.stulist li{border:1px solid var(--line);border-radius:10px;background:var(--surface);padding:12px 16px;display:flex;flex-direction:column;gap:2px;font-size:14.5px;color:var(--ink-2)}
.stulist li b{font-size:16px;color:var(--ink)}.stulist .prog{color:var(--ink-3);font-size:13.5px}
.spteaser{border:1px solid var(--line);border-left:4px solid var(--signal);border-radius:10px;background:var(--surface);padding:16px 20px;margin:0 0 28px;max-width:46em}
.spteaser h3{margin:0 0 6px;font-size:20px}.spteaser p{margin:0 0 10px;color:var(--ink-2)}.spkicker{font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin:0 0 6px}
.spwhos{display:flex;flex-wrap:wrap;gap:12px 28px}.spwho{display:flex;align-items:center;gap:12px}.spwho .avatar{width:56px;height:56px;border-radius:50%;object-fit:cover}.spwho b{display:block;font-size:15px}.spwho span{font-size:13px;color:var(--ink-3)}
.stu{display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px 22px 20px}
.stu .avatar{display:block;margin:0 auto 16px;width:180px;height:180px;font-size:40px}
.avatar.round{border-radius:50%;background:transparent}
.avatar.mono.round{background:var(--signal-tint)}
.stu h3{font-size:20px;margin-bottom:4px;text-align:center}
.stu>.ptitle{text-align:center}
.stu .focus{font-size:14.5px;color:var(--ink-2);margin:8px 0 8px}
.stu .pmeta{margin-bottom:0}
.stu .gsline{margin:6px 0 14px}
.stu .stufig{margin-top:auto}
.stupubs{font-size:13.5px;color:var(--ink-3);margin:2px 0 10px}
.stupubs b{color:var(--ink)}
.stupub{background:var(--bg-2);border-left:3px solid var(--signal);border-radius:0 8px 8px 0;padding:10px 12px;margin:0 0 12px;font-size:13.5px;line-height:1.4}
.stupub .lbl{display:block;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px}
.stupub .v{display:block;color:var(--ink-3);font-size:12.5px;margin-top:4px}
.stufig{margin:18px 0 0;align-self:stretch;background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px}
.stufig img{width:100%;height:150px;object-fit:contain;display:block}
.stufig .svgfig,.stufig img{margin-bottom:6px}
.stufig .svgfig{height:150px}
.stufig .svgfig svg{width:100%;height:100%;display:block}
.stufig figcaption{font-size:12px;line-height:1.35;color:#5B6B82;text-align:center;margin-top:0;min-height:2.7em;display:flex;align-items:center;justify-content:center}
.gsline{font-size:13px;color:var(--ink-3);margin:6px 0 0}
.gsline b{color:var(--ink)}
.stu.feat{display:grid;grid-template-columns:180px 1fr;gap:6px 22px;align-items:start}
.stu.feat h3,.stu.feat>.ptitle{text-align:left}
.stu.feat .avatar{margin:0}
.stu.feat .avatar{grid-row:1/4;margin:0}
.stu.feat .focus{grid-column:2}
@media (max-width:980px){.stugrid{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.stugrid,.stugrid.two{grid-template-columns:1fr}.stu.feat{grid-template-columns:1fr}.stu .avatar{width:150px;height:150px}.stu.feat .avatar{grid-row:auto;margin-bottom:12px}.stu.feat .focus{grid-column:auto}}
.lablife{margin-top:52px}
.lablife .grouph{font-size:22px;margin-bottom:4px}
.lablife>p{color:var(--ink-3);font-size:14.5px;margin-bottom:14px}
.labgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.labgrid img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:var(--radius);border:1px solid var(--line);display:block}
@media (max-width:760px){.labgrid{grid-template-columns:1fr 1fr}}
.alumcols{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(24px,5vw,64px)}
.alumcols .grouph{font-size:22px;margin-bottom:10px}
.alumlist{list-style:none;margin:0;padding:0;border-top:2px solid var(--ink)}
.alumlist li{display:grid;grid-template-columns:62px 1fr;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);font-size:15px}
.alumlist .yr{color:var(--ink-3);font-size:14px;padding-top:1px}
.alumlist.nodate li{grid-template-columns:1fr}
.alumlist .where{display:block;color:var(--ink-3);font-size:13.5px}
.giftbox h3{font-size:21px;margin-bottom:10px}
.giftbox p{font-size:15px;color:var(--ink-2);margin-bottom:16px}
.btn-gift{display:block;text-align:center;background:#0B5ED7;color:#fff;font-weight:600;padding:14px 20px;border-radius:6px;font-size:16px;max-width:36em}
.btn-gift:hover{text-decoration:none;background:#0A4FB5}
@media (max-width:860px){.alumcols{grid-template-columns:1fr}}

/* publications */
.filters{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-bottom:22px;padding:14px 18px;border:1px solid var(--line);border-radius:var(--radius);background:var(--bg-2)}
.fgroup{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.fgroup .lab{font-size:13.5px;color:var(--ink-3);margin-right:4px}
.chip{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:6px 13px;font:inherit;font-size:14px;color:var(--ink-2);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--bg)}
.chip:hover{border-color:var(--ink-2)}
.search{margin-left:auto;display:flex;align-items:center;gap:8px}
.search input{font:inherit;font-size:14.5px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);min-width:230px}
.count{font-size:14px;color:var(--ink-3);margin-bottom:14px}
.yearhead{font-family:"Fraunces",Georgia,serif;font-size:30px;font-weight:600;letter-spacing:-.02em;padding:22px 0 10px;border-bottom:2px solid var(--ink);margin-bottom:4px}
.pubs{list-style:none;margin:0 0 8px;padding:0}
.pubs li{padding:16px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:minmax(0,1fr) 140px;gap:8px 24px;align-items:start}
.pubs .t{font-weight:600;font-size:16.5px;line-height:1.35;display:block;margin:2px 0 4px;color:var(--ink)}
.pubs a.t:hover{color:var(--signal-2)}
.pubs .a{font-size:14.5px;color:var(--ink-2);line-height:1.45}
.pubs .v{font-size:14.5px;color:var(--ink-3);line-height:1.45}
.pubs .v i{font-style:italic;color:var(--ink-2)}
.pubs .side{font-size:13px;color:var(--ink-3);text-align:right;line-height:1.5;overflow-wrap:anywhere}
.pubs .side .kind{display:inline-block;padding:2px 8px;border-radius:4px;background:var(--line-2);color:var(--ink-2);font-size:12.5px;margin-bottom:6px}
.pubs .side .kind.j{background:var(--journal-bg);color:var(--journal-fg)}
.pubs .side .kind.c{background:var(--amber-2);color:var(--amber-text)}
.pubs .side a{display:block}
@media (max-width:640px){.pubs li{grid-template-columns:1fr}.pubs .side{text-align:left}.search{margin-left:0;width:100%}.search input{width:100%}}
.pubnote{font-size:13.5px;color:var(--ink-3);margin-top:18px;max-width:60em}

/* news */
.timeline{list-style:none;margin:0;padding:0;border-top:2px solid var(--ink)}
.timeline li{display:grid;grid-template-columns:120px minmax(0,1fr);gap:24px;padding:16px 0;border-bottom:1px solid var(--line)}
.timeline time{font-weight:600;font-size:14.5px;color:var(--ink-2);padding-top:2px}
.timeline p{margin:0;max-width:62em}
@media (max-width:640px){.timeline li{grid-template-columns:1fr;gap:4px}}

/* work with us */
.join{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:clamp(24px,5vw,64px);align-items:center}
.join .photo{border-radius:var(--radius);overflow:hidden;box-shadow:0 20px 50px -30px var(--shadow);aspect-ratio:4/3}
.join .photo img{width:100%;height:100%;object-fit:cover;display:block}
.join h3{margin-bottom:8px}
.join p{max-width:38em;color:var(--ink-2)}
.join ul{margin:0;padding-left:18px;color:var(--ink-2)}
.join li{margin-bottom:6px}
.join .block+.block{margin-top:26px;padding-top:22px;border-top:1px solid var(--line)}
@media (max-width:860px){.join{grid-template-columns:1fr}}

/* UML standard footer (matches uml.edu layout-footer) */
.uml-footer{background:#003870;color:#fff;font-family:"Barlow","IBM Plex Sans",Arial,sans-serif;border-top:1px solid rgba(255,255,255,.18);margin-top:0}
.uml-footer a{color:#fff}
.uml-footer .cols{display:grid;grid-template-columns:1.15fr 1fr 1fr 1fr;padding:44px 0 40px}
.uml-footer .col{padding:0 32px;border-left:1px solid rgba(255,255,255,.26)}
.uml-footer .col:first-child{padding-left:0;border-left:0}
.uml-footer .flogo{background:#fff;border-radius:10px;padding:12px 14px;width:190px;margin-bottom:18px}
.uml-footer .flogo img{width:100%;height:auto;display:block}
.uml-footer .uml-logo{width:56px;height:auto;display:block;margin-bottom:22px}
.uml-footer address{font-style:normal;font-size:14px;line-height:1.55;color:#C7D6E5}
.uml-footer address strong{color:#fff;font-weight:700;font-size:14.5px}
.uml-footer h2{font-family:"Barlow","IBM Plex Sans",Arial,sans-serif;font-weight:700;font-size:16px;letter-spacing:.06em;text-transform:uppercase;color:#fff;margin:0 0 10px}
.uml-footer .menu ul{list-style:none;margin:0;padding:0}
.uml-footer .menu li{margin:0 0 8px}
.uml-footer .menu a{font-size:18px;font-weight:400;color:#fff}
.uml-footer .menu a:hover{text-decoration:underline}
.uml-footer .dir p{margin:0;font-size:14px;line-height:1.6;color:#C7D6E5}
.uml-footer .dir a{color:#fff;text-decoration:underline;text-underline-offset:.15em}
.follow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:16px;font-size:14px}
.follow .lbl{color:#C7D6E5;margin-right:2px}
.follow a{display:inline-flex;align-items:center;gap:6px;color:#fff;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:6px 12px}
.follow a:hover{text-decoration:none;border-color:#fff}
.follow i{font-size:15px}
.follow-light{margin-top:22px;padding-top:18px;border-top:1px solid var(--line)}
.follow-light .lbl{color:var(--ink-3)}
.follow-light a{color:var(--ink);border-color:var(--line);background:var(--surface)}
.follow-light a:hover{border-color:var(--ink-3)}
.uml-footer .social{text-align:right}
.uml-footer .social ul{list-style:none;margin:0;padding:0;display:flex;justify-content:flex-end;gap:14px;flex-wrap:wrap}
.uml-footer .social a{display:inline-flex;width:36px;height:36px;align-items:center;justify-content:center;border-radius:50%;color:#C7D6E5;font-size:20px;border:1px solid transparent}
.uml-footer .social a:hover{color:#fff;border-color:rgba(255,255,255,.4);text-decoration:none}
.uml-footer .social .label{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.uml-footer .bottom{background:#003C72;border-top:1px solid rgba(255,255,255,.18);padding:18px 0 20px}
.uml-footer .bottom ul{list-style:none;margin:0;padding:0;display:flex;justify-content:center;gap:10px 26px;flex-wrap:wrap}
.uml-footer .bottom a{font-size:13.5px;text-decoration:underline;text-underline-offset:.18em;color:#fff}
.uml-footer .fine{text-align:center;font-size:12.5px;color:#9DB3CC;margin:14px 0 0}
.uml-footer .vsep{display:inline-block;width:1px;height:12px;background:rgba(255,255,255,.25);margin:0 10px;vertical-align:-2px}
#visits img{vertical-align:middle}
#visits:empty+.vsep,.vsep:has(+#visits:empty){display:none}
.version{text-align:center;font-size:12px;color:#A9BDD3;margin:6px 0 0;font-variant-numeric:tabular-nums}
.uml-footer .vsep::before{content:"\00b7";margin:0 10px}
.uml-footer #visits{display:inline-flex;vertical-align:-5px}
.uml-footer #visits img{height:20px;display:block}
@media (max-width:980px){.uml-footer .cols{grid-template-columns:1fr 1fr;gap:28px 0}.uml-footer .col{padding:0 24px}.uml-footer .col:nth-child(3){border-left:0;padding-left:0}.uml-footer .social{text-align:left}.uml-footer .social ul{justify-content:flex-start}}
@media (max-width:600px){.uml-footer .cols{grid-template-columns:1fr}.uml-footer .col{padding:0;border-left:0;border-top:1px solid rgba(255,255,255,.18);padding-top:22px}.uml-footer .col:first-child{border-top:0;padding-top:0}}
"""

UML_LOGO = '<svg class="uml-logo" width="311" height="393" role="img" aria-label="UMass Lowell" viewBox="0 0 311 393" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0_1035_48)"><path d="M13.8564 233.134C13.8564 186.343 137.109 94.7154 137.109 64.8359C137.109 54.7629 125.145 51.8364 112.776 51.8364C86.8412 51.8364 14.6486 83.0255 14.6486 129.171C14.6486 146.067 25.4169 155.493 45.7569 160.036C30.3806 168.476 8.58543 163.432 -0.0162354 148.864V255.366H27.438C19.2728 250.661 13.8402 241.833 13.8402 233.15L13.8564 233.134Z" fill="white"/><path d="M122.752 44.6899C137.028 44.6899 147.942 47.7457 155.202 52.2406L109.671 0H0V121.296C11.5767 94.0848 50.7854 44.6899 122.752 44.6899Z" fill="white"/><path d="M62.8633 255.35H114.425V226.02C97.658 239.23 80.0343 250.079 62.8633 255.35Z" fill="white"/><path d="M277.711 72.2249C252.294 99.8408 186.132 204.532 186.132 238.987C186.132 247.767 192.519 252.31 202.091 252.31C220.846 252.31 245.568 223.724 245.568 190.579C252.359 195.445 255.544 202.608 255.544 209.755C255.544 228.365 241.089 246.813 221.849 255.382H310.679V0H201.007L155.218 52.2406C163.335 57.4954 166.601 64.464 166.601 70.3494C166.601 103.479 40.9548 209.415 40.9548 238.648C40.9548 245.148 44.14 246.441 51.3189 246.441C109.154 246.441 210.078 109.865 239.974 72.1764L277.727 72.2249H277.711Z" fill="white"/><path d="M0.129272 301.964C0.129272 322.093 10.2023 328.997 28.3111 328.997C47.7295 328.997 56.412 320.8 56.412 302.044V268.996H37.2523V304.001C37.2523 310.339 35.215 314.721 28.3111 314.721C20.437 314.721 19.3052 309.773 19.3052 304.001V268.996H0.129272V301.964Z" fill="white"/><path d="M83.559 327.462V307.639L83.1548 298.552L82.3464 289.951H82.5081L93.147 327.462H106.47L117.109 289.951H117.27L116.284 300.493L116.042 309.595V327.462H133.261V268.996H110.124L99.8084 305.456L89.4929 268.996H66.3557V327.462H83.559Z" fill="white"/><path d="M178.113 268.996H158.613L137.659 327.462H156.415L158.597 319.749H177.676L179.94 327.462H199.035L178.08 268.996H178.113ZM162.284 307.558L168.218 286.604L174.394 307.558H162.3H162.284Z" fill="white"/><path d="M251.583 285.957C250.208 275.722 242.819 267.444 226.57 267.444C211.953 267.444 201.234 273.701 201.234 286.119C201.234 308.447 234.848 302.352 234.848 311.212C234.848 313.977 231.679 315.513 226.893 315.513C225.018 315.513 222.997 315.028 221.444 314.058C219.811 313.088 218.68 311.536 218.275 309.434H199.924C200.328 319.976 210.401 328.998 225.826 328.998C241.251 328.998 253.183 322.417 253.183 308.852C253.183 287.574 219.569 293.023 219.569 284.259C219.569 282.141 221.428 280.929 225.664 280.929C227.524 280.929 229.238 281.252 230.612 281.98C231.986 282.707 233.053 283.936 233.377 285.957H251.566H251.583Z" fill="white"/><path d="M309.127 285.957C307.736 275.722 300.363 267.444 284.114 267.444C269.497 267.444 258.778 273.701 258.778 286.119C258.778 308.447 292.392 302.352 292.392 311.212C292.392 313.977 289.223 315.513 284.437 315.513C282.562 315.513 280.541 315.028 278.988 314.058C277.372 313.088 276.224 311.536 275.819 309.434H257.468C257.872 319.976 267.945 328.998 283.37 328.998C298.795 328.998 310.743 322.417 310.743 308.852C310.743 287.574 277.129 293.023 277.129 284.259C277.129 282.141 278.988 280.929 283.225 280.929C285.084 280.929 286.798 281.252 288.172 281.98C289.563 282.707 290.614 283.936 290.937 285.957H309.127Z" fill="white"/><path d="M0 340.073H16.5566V378.134H40.3405V391.263H0V340.073Z" fill="white"/><path d="M67.6492 338.844C83.9794 338.844 94.8932 350.033 94.8932 365.652C94.8932 381.271 83.9794 392.459 67.6492 392.459C51.3189 392.459 40.4052 381.271 40.4052 365.652C40.4052 350.033 51.3189 338.844 67.6492 338.844ZM67.6492 379.718C71.8692 379.718 78.3366 377.067 78.3366 365.668C78.3366 354.269 71.8692 351.617 67.6492 351.617C63.4292 351.617 56.9617 354.269 56.9617 365.668C56.9617 377.067 63.4292 379.718 67.6492 379.718Z" fill="white"/><path d="M152.017 391.247H135.913L130.125 360.057H129.979L124.336 391.247H108.151L93.5513 340.057H109.801L116.349 371.666H116.494L122.962 340.057H137.562L143.884 372.103H144.029L150.723 340.057H167.054L152.001 391.247H152.017Z" fill="white"/><path d="M171.904 340.073H216.384V353.186H188.461V359.572H213.829V371.763H188.461V378.15H217.208V391.279H171.904V340.089V340.073Z" fill="white"/><path d="M224.064 340.073H240.62V378.134H264.404V391.263H224.064V340.073Z" fill="white"/><path d="M270.128 340.073H286.685V378.134H310.468V391.263H270.128V340.073Z" fill="white"/></g><defs><clipPath id="clip0_1035_48"><rect width="310.743" height="392.475" fill="white"/></clipPath></defs></svg>'
LOGO = """<svg viewBox="0 0 34 34" aria-hidden="true"><rect class="lg-bg" x="1.5" y="1.5" width="31" height="31" rx="6"/><circle class="lg-dot" cx="10" cy="10" r="2.6"/><circle class="lg-dot" cx="24" cy="10" r="2.6"/><circle class="lg-dot" cx="10" cy="24" r="2.6"/><circle cx="24" cy="24" r="2.6" fill="#E39A16"/><path class="lg-line" d="M10 10h14M10 10v14M24 10v14M10 24h14M10 10l14 14" stroke-width="1.4" fill="none" opacity=".85"/></svg>"""

# three-site federation diagram for the SUMMIT feature (abstract, not a map)
FEDERATION = """<svg viewBox="0 0 900 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SUMMIT federates testbed sites at UMass Lowell, NYU Tandon, and West Virginia University" font-family="IBM Plex Sans, Arial, sans-serif">
<g fill="none" stroke="#FFFFFF" stroke-opacity=".35" stroke-width="1.5"><path d="M190 60H400M500 60H710"/></g>
<g fill="none" stroke="#5FD0B6" stroke-width="2.6" stroke-linecap="round"><path class="fed-flow" d="M190 60H400"/><path class="fed-flow" d="M500 60H710" style="animation-delay:1.2s"/></g>
<g fill="#FFFFFF"><circle cx="150" cy="60" r="11"/><circle cx="450" cy="60" r="11"/><circle cx="750" cy="60" r="11"/></g>
<g fill="#0A777F"><circle cx="150" cy="60" r="5"/><circle cx="450" cy="60" r="5"/><circle cx="750" cy="60" r="5"/></g>
<g fill="#FFFFFF" font-size="15" font-weight="600" text-anchor="middle"><text x="150" y="98">UMass Lowell</text><text x="450" y="98">NYU Tandon</text><text x="750" y="98">West Virginia University</text></g>
<g fill="#C9D3E0" font-size="12.5" text-anchor="middle"><text x="150" y="34">lead site and instrument host</text><text x="450" y="34">Yuzhang Lin, Co-PI</text><text x="750" y="34">Anurag Srivastava, partner</text></g>
</svg>"""

# cyber-physical loop schematic (About section)
SCHEMATIC = """<svg viewBox="0 0 760 490" role="img" aria-labelledby="schemTitle schemDesc" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, Arial, sans-serif">
<title id="schemTitle">How a smart cyber-physical system closes the loop</title>
<desc id="schemDesc">Physical systems in energy, transportation, health care, and manufacturing are measured by sensors, connected over a secure network, understood by AI, and acted on safely, with people in the loop.</desc>
<defs>
  <marker id="arrI" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0E2036"/></marker>
  <marker id="arrS" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
</defs>

<!-- column headers -->
<g font-size="13" font-weight="600" fill="#5B6B82" letter-spacing=".02em">
  <text x="105" y="34" text-anchor="middle">THE PHYSICAL WORLD</text><text x="392" y="34" text-anchor="middle">A SECURE NETWORK</text><text x="622" y="34" text-anchor="middle">SMART DECISIONS</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M30 44h150M317 44h150M512 44h220"/></g>

<!-- domain cards -->
<g class="card">
  <rect x="30" y="56" width="150" height="84" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <g transform="translate(48,64) scale(.9)" fill="none" stroke="#044978" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 44V14l16-8 16 8v30M6 44h32M14 24h16M14 33h16"/>
  </g>
  <path d="M112 68l-10 16h8l-6 16 16-20h-8l6-12z" fill="#3BA995"/>
  <text x="105" y="130" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">Energy and power</text>
</g>
<g class="card">
  <rect x="30" y="158" width="150" height="84" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <g transform="translate(66,168) scale(.85)">
    <path d="M6 30h60l-9-17H16z" fill="#044978"/><path d="M0 30h72v8H0z" fill="#044978" opacity=".85"/>
    <circle cx="16" cy="40" r="6" fill="#fff" stroke="#044978" stroke-width="2"/><circle cx="56" cy="40" r="6" fill="#fff" stroke="#044978" stroke-width="2"/>
    <g fill="none" stroke="#3BA995" stroke-width="2" stroke-linecap="round"><path d="M28 8a10 10 0 0 1 16 0M22 2a18 18 0 0 1 28 0"/></g>
  </g>
  <text x="105" y="232" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">Transportation</text>
</g>
<g class="card">
  <rect x="30" y="260" width="150" height="84" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <circle cx="86" cy="294" r="17" fill="#0A777F"/><path d="M86 285v18M77 294h18" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
  <path d="M106 298h8l5-10 7 20 6-14 4 6h10" fill="none" stroke="#3BA995" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="105" y="334" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">Healthcare</text>
</g>
<g class="card">
  <rect x="30" y="362" width="150" height="84" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <g transform="translate(86,368) scale(.78)" fill="none" stroke="#044978" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M0 4h40v8H0zM15 12h10l-3 8h-4z"/><path d="M-4 46h48M0 39h40M4 32h32"/>
    <path d="M20 22v6" stroke="#3BA995" stroke-width="2.8"/><circle cx="20" cy="30" r="2.4" fill="#3BA995" stroke="none"/>
  </g>
  <text x="105" y="437" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">Additive manufacturing</text>
</g>

<!-- edge nodes -->
<g class="card">
  <rect x="212" y="83" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/><rect x="212" y="185" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/><rect x="212" y="287" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/><rect x="212" y="389" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/>
</g>
<g font-size="12.5" font-weight="600" fill="#0A777F" text-anchor="middle"><text x="243" y="102">sensors</text><text x="243" y="204">sensors</text><text x="243" y="306">sensors</text><text x="243" y="408">sensors</text></g>

<!-- sense links: card -> edge -->
<g fill="none" stroke="#D5DCE5" stroke-width="2"><path d="M180 98h32M180 200h32M180 302h32M180 404h32"/></g>
<g fill="none" stroke="#3BA995" stroke-width="2.6" stroke-linecap="round"><path class="flow" d="M180 98h32"/><path class="flow slow" d="M180 200h32"/><path class="flow" d="M180 302h32"/><path class="flow slow" d="M180 404h32"/></g>

<!-- network core -->
<g class="card">
  <circle cx="378" cy="241" r="74" fill="#fff" stroke="#044978" stroke-width="1.6"/>
  <circle cx="378" cy="241" r="74" fill="none" stroke="#0A777F" stroke-width="3" class="flow slow"/>
  <g stroke="#D5DCE5" stroke-width="1.2"><path d="M378 167v148M314 204l128 74M314 278l128-74"/></g>
  <g fill="#044978"><circle cx="378" cy="167" r="5.5"/><circle cx="442" cy="204" r="5.5"/><circle cx="442" cy="278" r="5.5"/><circle cx="378" cy="315" r="5.5"/><circle cx="314" cy="278" r="5.5"/><circle cx="314" cy="204" r="5.5"/></g>
  <circle cx="378" cy="241" r="14" fill="#0A777F"/><circle cx="378" cy="241" r="5" fill="#fff"/>
</g>
<text x="378" y="148" text-anchor="middle" font-size="12.5" fill="#5B6B82">fast, reliable links: fiber, 5G, 6G</text>
<text x="378" y="338" text-anchor="middle" font-size="12.5" fill="#5B6B82">every device verified, intrusions caught</text>

<!-- edge -> core links -->
<g fill="none" stroke="#D5DCE5" stroke-width="2"><path d="M274 98C296 98 302 170 316 200"/><path d="M274 200C290 200 298 221 306 226"/><path d="M274 302C290 302 298 261 306 256"/><path d="M274 404C296 404 302 312 316 282"/></g>
<g fill="none" stroke="#0A777F" stroke-width="2.6" stroke-linecap="round"><path class="flow" d="M274 98C296 98 302 170 316 200"/><path class="flow slow" d="M274 200C290 200 298 221 306 226"/><path class="flow" d="M274 302C290 302 298 261 306 256"/><path class="flow slow" d="M274 404C296 404 302 312 316 282"/></g>

<!-- compute card -->
<g class="card">
  <rect x="512" y="132" width="220" height="218" rx="14" fill="#fff" stroke="#D5DCE5"/>
  <rect x="512" y="132" width="220" height="44" rx="14" fill="#044978"/><rect x="512" y="160" width="220" height="16" fill="#044978"/>
  <text x="622" y="160" text-anchor="middle" font-size="14" font-weight="600" fill="#fff">AI that understands the system</text>
  <g fill="#F3F7FA" stroke="#D5DCE5"><rect x="528" y="190" width="188" height="34" rx="8"/><rect x="528" y="234" width="188" height="34" rx="8"/><rect x="528" y="278" width="188" height="34" rx="8"/></g>
  <g fill="none" stroke="#0A777F" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M540 212l6-8 5 5 6-10 5 6"/><path d="M539 256h8l4-8 4 12 4-6h8"/><path d="M540 302l7-7 5 5 9-9M563 291h-6v6"/>
  </g>
  <g font-size="12.5" fill="#0E2036"><text x="576" y="211">Spot trouble early</text><text x="576" y="255">Know the true state</text><text x="576" y="299">Decide and act safely</text></g>
  <g fill="#3BA995"><circle cx="702" cy="207" r="4" class="pulse"/><circle cx="702" cy="251" r="4" class="pulse" style="animation-delay:1s"/><circle cx="702" cy="295" r="4" class="pulse" style="animation-delay:2s"/></g>
  <text x="622" y="336" text-anchor="middle" font-size="12" fill="#5B6B82">from the device to the cloud</text>
</g>

<!-- core <-> compute -->
<g fill="none" stroke="#0A777F" stroke-width="2.2"><path d="M454 226h50" marker-end="url(#arrS)"/></g>
<g fill="none" stroke="#3BA995" stroke-width="2.2"><path d="M506 256h-50" marker-end="url(#arrG)"/></g>
<text x="481" y="215" text-anchor="middle" font-size="11.5" fill="#5B6B82">data</text>
<text x="481" y="275" text-anchor="middle" font-size="11.5" fill="#5B6B82">decisions</text>

<!-- return loop -->
<path d="M622 350v106H105v-6" fill="none" stroke="#3BA995" stroke-width="2" stroke-dasharray="5 6" marker-end="url(#arrG)"/>
<text x="392" y="480" text-anchor="middle" font-size="12.5" fill="#5B6B82">Sense. Communicate. Decide. Act. People stay in the loop.</text>
</svg>"""

ICONS = {
    "grid": '<svg viewBox="0 0 40 40"><path d="M6 34V14l14-8 14 8v20M6 34h28M14 22h12M14 28h12"/><path d="M4 36h32"/></svg>',
    "ai": '<svg viewBox="0 0 40 40"><rect x="8" y="8" width="24" height="24" rx="4"/><path d="M16 8V4M24 8V4M16 36v-4M24 36v-4M8 16H4M8 24H4M36 16h-4M36 24h-4"/><path d="M15 20h10M20 15v10"/></svg>',
    "fiber": '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="14"/><path d="M6 20h28M20 6c6 6 6 22 0 28M20 6c-6 6-6 22 0 28"/></svg>',
    "edge": '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="4"/><circle cx="8" cy="10" r="3"/><circle cx="32" cy="10" r="3"/><circle cx="8" cy="30" r="3"/><circle cx="32" cy="30" r="3"/><path d="M11 12l6 5M29 12l-6 5M11 28l6-5M29 28l-6-5"/></svg>',
    "chip": '<svg viewBox="0 0 40 40"><rect x="12" y="12" width="16" height="16" rx="2"/><path d="M16 12V6M20 12V6M24 12V6M16 34v-6M20 34v-6M24 34v-6M12 16H6M12 20H6M12 24H6M34 16h-6M34 20h-6M34 24h-6"/></svg>',
    "health": '<svg viewBox="0 0 40 40"><path d="M4 22h8l4-10 6 18 4-10h10"/><rect x="6" y="6" width="28" height="28" rx="5"/></svg>',
}


# Longer material for each thrust page: the question the thrust asks, what the group actually builds,
# and which projects and tools belong to it. Keys match THRUSTS.
THRUST_DETAIL = {
    "grid": {
        "question": "What happens to a power grid when the computers and networks that run it are attacked, and how does it get back?",
        "lede": "Modern distribution and transmission systems are steered by measurements that travel over networks. That makes the measurement path itself an attack surface: corrupt what the operator sees and you corrupt what the operator does. The center studies the whole loop, from the meter to the control room and back out to the breaker.",
        "work": [
            ("Detecting false data before it reaches control", "Smart meters and phasor measurement units can be spoofed. The group builds detectors, both centralized and federated across sites, that flag injected measurements without needing to pool raw data from every utility."),
            ("Observability-aware communication design", "Where PMUs sit and how their traffic is routed determines whether the state estimator can still see the grid after a failure. The group co-designs sensor placement and network topology rather than treating them as separate problems."),
            ("Joint power and communication restoration", "After a storm or an attack, the power layer and the communication layer have to come back together: a crew cannot reconfigure what it cannot observe. The group formulates restoration as one problem across both layers, including networked microgrid formation."),
            ("Experiments on real hardware", "Claims about resilience are only as good as the testbed behind them. SUMMIT couples RTDS real-time simulation with actual controllers, relays, and network equipment across three universities."),
        ],
        "projects": ["SUMMIT", "Unified Post-Disaster Restoration", "CyberCARED", "Resilient Smart Grids", "Software-Defined Cyber-Physical Microgrids"],
    },
    "ai": {
        "question": "When an AI system can move something physical, what keeps it inside the envelope?",
        "lede": "Machine learning is now embedded in decisions that open breakers, route traffic, and provision networks. Accuracy on a benchmark says little about behavior during an attack, a sensor fault, or a distribution shift. The center works on models that respect the physics of the system they control and on enforcement that sits between a model's output and the actuator.",
        "work": [
            ("Learning-based intrusion and anomaly detection", "Scalable, real-time detection of attacks on grid control traffic, including adaptive transfer learning so a detector trained on one network still works on the next."),
            ("Federated learning across operators", "Utilities cannot share raw operational data. Federated training lets detection models improve across sites while the measurements stay home, and the group measures what that costs in accuracy."),
            ("Physics-grounded models", "A model that ignores power flow or optical impairment will confidently propose something impossible. The group grounds learned models in the physical constraints of the system."),
            ("Safety enforcement for agentic systems", "As AI agents take actions rather than make predictions, the question becomes what the agent is permitted to do. The group works on enforcement layers that check actions against safety properties before they reach infrastructure."),
        ],
        "projects": ["ARPO-Sensor Fusion", "ARPO", "CyberCARED"],
    },
    "fiber": {
        "question": "How do we get an order of magnitude more capacity out of deployed fiber without giving up service quality?",
        "lede": "Traffic growth outpaces the capacity of the C band. The next increment comes from using more of the spectrum and more spatial paths in the same fiber, which makes provisioning far harder: impairments differ by band, by core, and by path. The center builds the algorithms and the open tools for that regime.",
        "work": [
            ("Multi-band and space-division multiplexing", "Routing, modulation, core, band, and spectrum assignment treated as one allocation problem, with the trade-off between spectral and spatial scaling measured rather than assumed."),
            ("Quality-of-transmission-aware allocation", "Provisioning that accounts for physical-layer impairments, including nonlinear interference that grows with load, so a lightpath is not accepted and then quietly fails."),
            ("Service prioritization for 6G transport", "Fronthaul and backhaul for 6G impose latency and reliability classes on the optical layer; the group studies how to honor them under load."),
            ("Open-source, reproducible research", "FUSION is a benchmarking and simulation framework built so results in this field can be reproduced and compared rather than taken on faith."),
        ],
        "projects": ["Flexible Spectrum Allocation", "PROPER", "COMMON", "CARGONET", "SOON"],
        "tools": [("FUSION", "https://github.com/SDNNetSim/FUSION", "Open-source optical network simulation and benchmarking")],
    },
    "edge": {
        "question": "How do distributed systems keep agreeing when machines crash, links fail, and some nodes are hostile?",
        "lede": "Cyber-physical systems increasingly run on clusters at the edge rather than a single controller. That buys resilience only if the replicas can agree under adversarial conditions, at latencies a physical process can tolerate. The center works on the protocols and the systems that make that true.",
        "work": [
            ("Fault-tolerant consensus and state machine replication", "Protocols that stay correct and fast when replicas crash or misbehave, with the latency budgets that control loops actually impose."),
            ("Blockchain and decentralized coordination", "Where a shared, tamper-evident record is worth its cost, and where it is not."),
            ("Satellite and drone edge coordination", "Coordination when connectivity is intermittent and nodes move, including satellite-edge and aerial platforms."),
            ("Digital twins from hybrid clouds", "Delivering twin fidelity from a mix of on-premise and cloud resources without breaking real-time guarantees."),
        ],
        "projects": ["Tseng NSF CAREER", "SUMMIT"],
    },
    "chip": {
        "question": "If the software stack is trustworthy but the silicon lies, what have you actually secured?",
        "lede": "Grid edge devices, embedded controllers, and HPC nodes are all built on hardware that can be modified, faulted, or silently wrong. The center works at that layer: finding trojans before tape-out, catching corruption that leaves no error, and giving a remote verifier a reason to trust a device.",
        "work": [
            ("Hardware trojan detection at RTL", "Finding malicious logic in a design before it becomes silicon, where it can still be removed."),
            ("Silent data corruption detection", "Corruption that produces a wrong answer without an error signal is the hardest fault in a large system. The group detects it from hardware performance counters, at a cost low enough to leave on."),
            ("Attested embedded devices", "Remote attestation for the small devices at grid edges, so a controller can prove what it is running."),
            ("Parallel I/O for data-intensive science", "High-performance storage and I/O paths for simulation and analysis at scale, including compression that preserves what the science needs."),
        ],
        "projects": ["SUMMIT", "Unified Post-Disaster Restoration"],
    },
    "nuclear": {
        "question": "How do you secure a facility where the consequences of being wrong are measured in decades?",
        "lede": "Nuclear energy is returning to the center of the decarbonization conversation, and with it the questions of safeguards, physical and cyber security, and who is trained to run these systems. The center's nuclear work sits alongside its grid and AI work rather than apart from it: a reactor is a cyber-physical system with an unusually long shadow.",
        "work": [
            ("Safeguards measurement and detector modeling", "Modeling detector response for safeguards verification, and the measurement campaigns that support it, alongside the UMass Lowell research reactor."),
            ("Security of nuclear facilities", "Physical and cyber security for facilities where an incident is not recoverable, including the analysis of security incidents at nuclear plants."),
            ("Robotics for environments people should not enter", "Robotic platforms for inspection and response inside nuclear facilities, developed with national laboratory partners."),
            ("Policy and training", "The Massachusetts Advanced Nuclear and Fusion Energy Roadmaps for the Commonwealth, and the IAEA-funded Intercontinental Nuclear Institute, which trains early-career professionals internationally."),
        ],
        "projects": ["Massachusetts Advanced Nuclear and Fusion Energy Roadmaps", "Intercontinental Nuclear Institute"],
    },
    "hpc": {
        "question": "If a machine gives you the wrong answer and no error, how would you ever know?",
        "lede": "The hardest fault in a large computing system is the one that produces a plausible wrong answer and raises nothing. At the scale modern simulation and analysis run, that is not a rare event. The center works on detecting corruption that leaves no trace, on encoding data so it stays usable and verifiable, and on the I/O paths that decide whether a result can be reproduced at all.",
        "work": [
            ("Silent data corruption detection", "Corruption that produces a wrong answer without an error signal, detected from hardware performance counters at a cost low enough to leave running in production."),
            ("Reliable and efficient data encoding", "Encoding schemes that keep simulation and analysis data usable, compact, and verifiable at extreme scale, funded by an NSF CAREER award."),
            ("Data integrity for HPC datasets", "Using the sparsity structure of scientific datasets to find and correct corruption, with an NSF OAC Core award held jointly with the hardware security thrust."),
            ("Parallel I/O for data-intensive science", "The storage and I/O paths that decide whether a large computation can be checkpointed, restarted, and reproduced."),
        ],
        "projects": ["Improving Data Integrity", "Reliable and Efficient Data Encoding"],
    },
    "health": {
        "question": "What does this loop look like in a hospital, on a highway, on a bridge, and inside a reactor building?",
        "lede": "The same sense-communicate-decide-act loop shows up wherever computation meets a physical system, and each domain stresses it differently: latency on a highway, privacy in a hospital, harsh environments on a bridge, regulation in a nuclear facility. The center's breadth across colleges is what lets it work in all four.",
        "work": [
            ("Intelligent traffic and vehicular computing", "Connected and automated vehicles, trajectory prediction, crosswalk and roadway condition assessment from aerial imagery, and the networks that carry it."),
            ("Medical imaging and digital health", "Image reconstruction from limited data, multimodal deep learning, and platforms that move clinical data safely."),
            ("Structural health monitoring", "Sensing and diagnostics for wind turbine blades, bridges, and buildings, including acoustic and vibration methods and drone-based inspection."),
            ("Human-robot interaction", "How people decide whether to trust a robot and what a robot owes them in return: trust calibration and repair, transparency in shared control, multi-robot coordination, and autonomy in marine and field settings."),
            ("Nuclear security and robotics", "Safeguards modeling, security of nuclear facilities, and robotic platforms for environments people should not enter."),
        ],
        "projects": ["Massachusetts Advanced Nuclear and Fusion Energy Roadmaps", "Intercontinental Nuclear Institute", "ARPO"],
    },
}

THRUSTS = [
    ("grid", "Smart grid cybersecurity and resilience",
     "Attack-aware dispatch, false-data-injection detection in smart meters, observability-aware PMU networking, and joint power-communication restoration after disasters. Anchored by the SUMMIT federated testbed.",
     "Vokkarane, Arias, Tseng, Lin"),
    ("ai", "AI and agentic systems for cyber-physical control",
     "Machine learning for intrusion detection and state recovery, physics-grounded models for network provisioning, and safety enforcement for AI agents that touch physical infrastructure.",
     "Luo, Cao, Vokkarane, Son"),
    ("fiber", "Next-generation optical and 6G transport",
     "Multi-band and space-division multiplexed elastic optical networks, quality-of-transmission-aware resource allocation and grooming, service prioritization for 6G transport, and the open-source FUSION framework.",
     "Vokkarane, Chigan"),
    ("edge", "Fault-tolerant distributed and edge computing",
     "Consensus and state machine replication that stay correct under crashes and attacks, blockchain systems, satellite-edge drone coordination, and digital twins delivered from hybrid clouds.",
     "Tseng, Luo"),
    ("chip", "Hardware security and trusted devices",
     "Hardware trojan detection at RTL, attested embedded devices for grid edges, and authentication for printed and flexible electronics.",
     "Arias, Akyurtlu, Ranasingha"),
    ("hpc", "High performance computing and data integrity",
     "Detecting silent data corruption from hardware counters, reliable and efficient encoding for extreme-scale simulation, and the parallel I/O that data-intensive science runs on.",
     "Son, Luo"),
    ("health", "Connected transportation, health, and infrastructure",
     "Intelligent traffic and vehicular computing, medical imaging and digital health platforms, structural health monitoring for blades, bridges, and buildings, and robots that work alongside people.",
     "Xie, Luo, Cao, Yu, Inalpolat, Robinette, Niezrecki"),
    ("nuclear", "Nuclear energy and security",
     "Safeguards measurement and detector modeling, security of nuclear facilities, robotic platforms for environments people should not enter, and the training that supports them.",
     "Aghara, Niezrecki"),
]



# ---------------------------------------------------------------- students and alumni (from the director's CV, Sept. 2026)
STUDENTS = [
    {"name": "Arash Rezaee", "advisor": "Vinod M. Vokkarane", "photo": "arash", "fig": "fig_arash", "figcap": "AI services over a software-defined, multi-layer network", "status": "Ph.D. Candidate, joined 2022", "focus": "AI-driven resource allocation in optical networks; impairment-aware provisioning in multi-band, space-division multiplexed networks; spectral versus spatial capacity scaling; reproducible optical network benchmarking with FUSION.", "linkedin": ""},
    {"name": "Ryan McCann", "advisor": "Vinod M. Vokkarane", "photo": "ryan", "fig": "fig_ryan", "figcap": "FUSION: reinforcement learning over a software-defined optical mesh", "status": "Ph.D. Candidate, joined 2024", "focus": "Co-founder and lead developer of FUSION (github.com/SDNNetSim/FUSION), supported by MIT I-Corps and AT&T; reinforcement learning for software-defined elastic optical networks; failure-aware routing and realistic simulation of elastic optical and mesh networks.", "linkedin": ""},
    {"name": "Kenneth Patrick Watts", "advisor": "Vinod M. Vokkarane", "photo": "ken", "fig": "fig_ken", "figcap": "NATIG co-simulation of a distribution grid and its wireless network", "status": "Ph.D. Candidate, joined 2022", "focus": "Scalable, real-time detection of cyber attacks on smart power grids with machine learning; adaptive transfer learning for day-zero network intrusion detection; the NATIG cyber-physical co-simulation testbed (HELICS, GridLAB-D, ns-3).", "linkedin": ""},
    {"name": "Mehran Sasaninia", "advisor": "Vinod M. Vokkarane", "photo": "mehran", "fig": "fig_mehran", "figcap": "Federated learning across grid sites with a global model aggregator", "status": "Ph.D. Candidate, joined 2023", "focus": "Federated learning to detect cyber attacks in the smart grid; smart false data injection attacks and anomaly detection in smart meters (IEEE SmartGridComm 2025); centralized versus federated learning for grid anomaly detection.", "linkedin": ""},
    {"name": "Ayush Pandey", "advisor": "Vinod M. Vokkarane", "photo": "ayush", "status": "Ph.D. Student, joined 2024", "figsvg": "ayush", "figcap": "AI-based intrusion detection protecting a transmission grid's control loop", "focus": "Smart grid cybersecurity and AI for cyber-physical systems.", "linkedin": ""},
    {"name": "Suvhasis Mukhopadhyay", "advisor": "Vinod M. Vokkarane", "photo": "suvhasis", "figsvg": "suvhasis", "figcap": "Impairment-aware allocation of spectrum, modulation, and power on a flex-grid link", "status": "Ph.D. Student, joined 2024", "focus": "Impact of individual physical layer impairments on elastic optical network performance; impairment-aware routing, spectrum, modulation, and power allocation; dynamic optical networking.", "linkedin": ""},
    # Other center faculty's doctoral students, from their CVs (Sept. 2026). Program and dates as listed there;
    # Luo's CV gives expected graduation dates but not programs.
    {"name": "Zahra Sharifi Soltani", "advisor": "Orlando Arias", "status": "Ph.D. student", "program": "", "focus": ""},   # confirmed by the director, Sept. 2026
    {"name": "Timothy Miskell", "advisor": "Yan Luo", "status": "Ph.D. student, expected Nov. 2026", "program": "", "focus": ""},
    {"name": "Calvin Ng", "advisor": "Yan Luo", "status": "Ph.D. student, expected Aug. 2027", "program": "", "focus": ""},
    {"name": "Ali Alkhatatbih", "advisor": "Yan Luo", "status": "Ph.D. student, expected Aug. 2027", "program": "", "focus": ""},
    {"name": "Sage Lyon", "advisor": "Yan Luo", "status": "Ph.D. student, expected Dec. 2027", "program": "", "focus": ""},
    {"name": "Mohammad Shakhawat Hossain Fahim", "advisor": "Yan Luo", "status": "Ph.D. student, expected Dec. 2028", "program": "", "focus": ""},
    {"name": "Negin Yazdani Motlagh", "advisor": "Lewis Tseng", "status": "Ph.D. student, joined 2024", "program": "School of Education", "focus": ""},
    {"name": "Kritee Neupane", "advisor": "Lewis Tseng", "status": "Ph.D. student, joined 2025", "program": "Electrical and Computer Engineering", "focus": ""},
    {"name": "Layann Shaban", "advisor": "Lewis Tseng", "status": "Ph.D. student, joined 2026", "program": "Electrical and Computer Engineering", "focus": ""},
    {"name": "Youlim Lee", "advisor": "Lewis Tseng", "status": "Ph.D. student, joined 2026", "program": "School of Education", "focus": ""},
]

# ---------------------------------------------------------------- alumni profiles
# Verified Sept. 2026 against the sources named in each entry. "inst" is the degree institution when
# it is not UMass Lowell; "era" marks postdocs held at UMass Dartmouth before the 2013 move.
# Portraits: drop a file named portraits/<slug>.jpg beside build_site.py and it is embedded on the
# next build; the slug is the lowercase surname (islam.jpg, edib.jpg, cui.jpg ...). No portrait,
# no photo: nothing is scraped from LinkedIn or Scholar.
ALUMNI_PROFILES = {
    "Md Zahidul Islam": {"slug": "islam", "degree": "Ph.D. 2025", "inst": "New York University",
        "path": "Began doctoral research at UMass Lowell with Yuzhang Lin and Vokkarane; completed the degree at NYU after his advisor moved",
        "role": "Assistant Professor, School of Electrical, Computer, and Biomedical Engineering", "org": "Southern Illinois University Carbondale",
        "focus": "Smart grid monitoring, cyber-physical resilience, and AI for power systems; NEC Labs America and NREL collaborations",
        "linkedin": "https://www.linkedin.com/in/zahidul-nyu25/", "scholar": "i_ebAeUAAAAJ", "web": "https://zahidul-ece.github.io/",
        "src": "SIU faculty page, personal site, LinkedIn, Scholar"},
    "Shamsun Nahar Edib": {"slug": "edib", "degree": "Ph.D. 2024", "inst": "",
        "path": "Primary advisor Yuzhang Lin; Best Ph.D. Student Award",
        "role": "Assistant Professor, Electrical and Computer Engineering", "org": "Montana State University",
        "focus": "Cyber-physical resilience, smart grid monitoring, and power system restoration",
        "linkedin": "https://www.linkedin.com/in/shamsun-nahar-edib/", "scholar": "xgysIYIAAAAJ", "web": "https://shamsun-edib.github.io/",
        "src": "Montana State catalog, personal site, LinkedIn, Scholar"},
    "Travis Kessler": {"slug": "kessler", "degree": "Ph.D. 2023", "inst": "",
        "path": "Primary advisor Hunter Mack; Best Ph.D. Student Award",
        "role": "Research Engineer", "org": "AIMdyn, Inc.",
        "focus": "Applied machine learning for fuel property prediction, MLOps, and goal-directed agents in simulation",
        "linkedin": "https://www.linkedin.com/in/traviskessler/", "scholar": "", "web": "https://www.traviskessler.com/",
        "src": "AIMdyn LinkedIn post, personal site, ResearchGate"},
    "Yue Wang": {"slug": "wang", "degree": "Ph.D. 2022", "inst": "",
        "path": "Dissertation on dynamic traffic scheduling with spectral and spatial flexibility in SDM elastic optical networks; advisor Vokkarane",
        "role": "Software Engineer", "org": "KLA",
        "focus": "Elastic optical networks and space-division multiplexing",
        "linkedin": "", "scholar": "fu07D-gAAAAJ", "web": "",
        "src": "UMass Lowell defense notice, Scholar; LinkedIn profile not confirmed (two candidates)"},
    "Pegah Afsharlar": {"slug": "afsharlar", "degree": "Ph.D. 2020", "inst": "",
        "path": "Advisor Vokkarane; Best Paper Award, IEEE ANTS 2016; Top Paper Award, ONDM 2016",
        "role": "Data Scientist", "org": "",
        "focus": "Delayed spectrum allocation and anycast advance reservation in elastic optical networks",
        "linkedin": "", "scholar": "", "web": "",
        "src": "Francis College of Engineering Solutions magazine, director's site; current employer not confirmed"},
    "Yan Cui": {"slug": "cui", "degree": "Ph.D. 2019", "inst": "",
        "path": "Advisor Vokkarane; taught at San José State University 2019 to 2022",
        "role": "Lecturer, Computer Science and Engineering", "org": "Santa Clara University",
        "focus": "Architectures and algorithms for ultra-high-speed networks; machine learning in networking",
        "linkedin": "https://www.linkedin.com/in/yan-cui-04862278/", "scholar": "nAVlj58AAAAJ", "web": "https://www.scu.edu/engineering/faculty/cui-yan/",
        "src": "Santa Clara University faculty page and bulletin, LinkedIn, Scholar"},
    "Dylan A. P. Davis": {"slug": "davis", "degree": "Ph.D. 2018", "inst": "",
        "path": "Advisor Vokkarane; Best Paper Award, ONDM 2015",
        "role": "Senior Software Engineer", "org": "Hitachi Vantara",
        "focus": "Survivable multicast and manycast routing; path computation and resource reservation for research networks",
        "linkedin": "https://www.linkedin.com/in/dylanapdavis/", "scholar": "HL3j-7sAAAAJ", "web": "",
        "src": "LinkedIn, ZoomInfo, Scholar, director's CV"},
    "Arash Deylamsalehi": {"slug": "deylamsalehi", "degree": "Ph.D. 2017", "inst": "",
        "path": "Advisor Vokkarane; postdoctoral researcher in the group afterward",
        "role": "Quantitative Network Analyst", "org": "Google",
        "focus": "Energy cost and emissions-aware routing in optical networks; machine learning for network operation",
        "linkedin": "https://www.linkedin.com/in/arashdeylam/", "scholar": "VobjklIAAAAJ", "web": "",
        "src": "LinkedIn, Scholar, director's CV"},
    "Jeremy M. Plante": {"slug": "plante", "degree": "Ph.D. 2017", "inst": "",
        "path": "Advisor Vokkarane; Best ECE Graduate Student Award 2015 to 2016; postdoctoral researcher in the group afterward",
        "role": "Software engineer", "org": "Hitachi Vantara",
        "focus": "Sliding scheduled lightpaths and parallel circuit provisioning in ESnet's OSCARS",
        "linkedin": "", "scholar": "oYnitXIAAAAJ", "web": "",
        "src": "Director's CV and site, Scholar; LinkedIn not located"},
    "Amir Ehsani Zonouz": {"slug": "zonouz", "degree": "Ph.D. 2015", "inst": "University of Massachusetts Dartmouth",
        "path": "Advisors Liudong Xing and Vokkarane, before the director moved to Lowell",
        "role": "AI and IoT", "org": "Accenture; founder and former CEO, airXsys",
        "focus": "Reliability of wireless sensor networks; deep learning and optimization",
        "linkedin": "https://www.linkedin.com/in/amir-ehsani-zonouz-a9724332/", "scholar": "WUi_j6AAAAAJ", "web": "",
        "src": "LinkedIn, Scholar, Mathematics Genealogy Project"},
    "Thilo Schöndienst": {"slug": "schoendienst", "degree": "Ph.D. 2014", "inst": "",
        "path": "Advisor Vokkarane, 2011 to 2014",
        "role": "Patent examiner", "org": "European Patent Office",
        "focus": "Renewable-energy-aware grooming and power-source-aware routing in optical networks",
        "linkedin": "", "scholar": "7X5H3_YAAAAJ", "web": "",
        "src": "Director's CV, Scholar (verified email at epo.org); title inferred from employer"},
    "Juzi Zhao": {"slug": "zhao", "degree": "Postdoctoral researcher 2015 to 2017", "inst": "",
        "path": "Ph.D. George Washington University 2015; Chalmers University before Lowell",
        "role": "Assistant Professor, Electrical Engineering", "org": "San José State University",
        "focus": "Optical networks, data center networks, and software-defined networking; NSF NeTS award as PI",
        "linkedin": "https://www.linkedin.com/in/juzi-zhao-ba733776/", "scholar": "9RfENp0AAAAJ", "web": "https://www.sjsu.edu/people/juzi.zhao/",
        "src": "SJSU faculty page and CV, LinkedIn, Scholar"},
    "Arush Gadkar": {"slug": "gadkar", "degree": "Postdoctoral researcher", "inst": "", "era": "at UMass Dartmouth",
        "path": "Ph.D. George Washington University",
        "role": "Registered Patent Agent", "org": "Kilpatrick Townsend & Stockton LLP",
        "focus": "Anycast advance reservation and multicast overlays in optical networks; now patent prosecution in software, hardware, and quantum computing",
        "linkedin": "https://www.linkedin.com/in/arush-gadkar-3565636/", "scholar": "KOQPJJAAAAAJ", "web": "https://ktslaw.com/en/People/G/GadkarArush",
        "src": "Kilpatrick Townsend profile, LinkedIn, Scholar"},
    "Joan Triay": {"slug": "triay", "degree": "Postdoctoral researcher 2010 to 2011", "inst": "", "era": "at UMass Dartmouth",
        "path": "Fulbright Scholar from Spain; advance reservation in WDM networks",
        "role": "Specialist", "org": "DOCOMO Euro-Labs",
        "focus": "Multi-access edge computing and network standardization",
        "linkedin": "", "scholar": "", "web": "",
        "src": "Director's CV; DOCOMO Euro-Labs role last seen in a 2018 conference listing"},
    "Balagangadhar Bathula": {"slug": "bathula", "degree": "Postdoctoral researcher 2007 to 2010", "inst": "", "era": "at UMass Dartmouth",
        "path": "Impairment-aware optical networks",
        "role": "Network Cloud and Infrastructure", "org": "AT&T",
        "focus": "Optical networking and network infrastructure",
        "linkedin": "", "scholar": "1c-DqjsAAAAJ", "web": "",
        "src": "Scholar (verified email at att.com), director's CV"},
}

ALUMNI_FEATURED = [
    {"name": "Md Zahidul Islam", "photo": "zahidul", "degree": "Ph.D. 2025, NYU (began at UMass Lowell)", "role": "Assistant Professor", "org": "Southern Illinois University Carbondale", "focus": "Resilient PMU networking and cyber-physical restoration of power distribution systems. Primary advisor Yuzhang Lin.", "linkedin": ""},
    {"name": "Shamsun Nahar Edib", "photo": "shamsun", "degree": "Ph.D. 2024", "role": "Assistant Professor", "org": "Montana State University", "focus": "Cross-domain resilient sensing and communication architectures for power grid monitoring. Primary advisor Yuzhang Lin. Best Ph.D. Student Award.", "linkedin": ""},
]
ALUMNI_PHD_OLD = [
    ("2025", "Md Zahidul Islam", "Assistant Professor, Southern Illinois University Carbondale; primary advisor Yuzhang Lin"),
    ("2024", "Shamsun Nahar Edib", "Assistant Professor, Montana State University; primary advisor Yuzhang Lin; Best Ph.D. Student Award"),
    ("2023", "Travis Kessler", "AIMdyn, Inc.; primary advisor Hunter Mack; Best Ph.D. Student Award"),
    ("2022", "Yue Wang", "KLA"),
    ("2020", "Pegah Afsharlar", "Data Scientist"),
    ("2019", "Yan Cui", "Santa Clara University"),
    ("2018", "Dylan A. P. Davis", "Hitachi Vantara"),
    ("2017", "Arash Deylamsalehi", "Google"),
    ("2017", "Jeremy M. Plante", "Hitachi Vantara; Best Ph.D. Student Award"),
    ("2015", "Amir Ehsani Zonouz", "AirSys"),
    ("2014", "Thilo Schöndienst", "European Patent Office"),
]
ALUMNI_POSTDOC = [("Arash Deylamsalehi", "Google"), ("Jeremy M. Plante", "Hitachi Vantara"), ("Juzi Zhao", "San José State University"), ("Arush Gadkar", "Kilpatrick Townsend & Stockton LLP"), ("Joan Triay", "DOCOMO Euro-Labs"), ("Balagangadhar Bathula", "AT&T")]
ALUMNI_PHD = [(p["degree"].split()[-1], n, "") for n, p in ALUMNI_PROFILES.items() if p["degree"].startswith("Ph.D.")]
ALUMNI_PHD.sort(key=lambda t: -int(t[0]))
FONT_ROOT = ""   # newsletter pages set this to "../" so the fonts resolve from the subfolder
SITE_URL = "https://smartcyberphysical.org/"   # the live address; feeds canonical links, sitemap, feeds
SITE_VERSION = "1.28"   # bump by 0.01 with every update to the site
GIFT_URL = "https://securelb.imodules.com/s/1355/lowell/forms/forms.aspx?sid=1355&gid=4&pgid=893&cid=2172&dids=2083&bledit=1&appealcode=ALUWEBSITE"

# Center social accounts. Paste the full profile URLs here; the "Follow SCyPS" links appear in the
# footer and the contact block only for entries that are filled in.
SOCIAL = {
    "linkedin": "",   # e.g. https://www.linkedin.com/company/<page-name>
    "x": "",          # e.g. https://x.com/<handle>
}
def social_links(cls="follow"):
    items = []
    if SOCIAL.get("linkedin"):
        items.append(f'<a href="{esc(SOCIAL["linkedin"])}" title="SCyPS on LinkedIn"><svg class="ico" viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"/></svg><span>LinkedIn</span></a>')
    if SOCIAL.get("x"):
        items.append(f'<a href="{esc(SOCIAL["x"])}" title="SCyPS on X"><svg class="ico" viewBox="0 0 512 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M389.2 48h70.6L305.6 224.2 487 464H345L233.7 318.6 106.5 464H35.8L200.7 275.5 26.8 48H172.4L272.9 180.9 389.2 48zM364.4 421.8h39.1L151.1 88h-42L364.4 421.8z"/></svg><span>X</span></a>')
    items.append(f'<a href="{SITE_URL}feed.xml" title="News feed for readers and posting tools"><svg class="ico" viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M0 64C0 46.3 14.3 32 32 32c229.8 0 416 186.2 416 416c0 17.7-14.3 32-32 32s-32-14.3-32-32C384 253.6 226.4 96 32 96C14.3 96 0 81.7 0 64zM0 416a64 64 0 1 1 128 0A64 64 0 1 1 0 416zM32 160c159.1 0 288 128.9 288 288c0 17.7-14.3 32-32 32s-32-14.3-32-32c0-123.7-100.3-224-224-224c-17.7 0-32-14.3-32-32s14.3-32 32-32z"/></svg><span>RSS</span></a>')
    return f'<div class="{cls}"><span class="lbl">Follow SCyPS</span>{"".join(items)}</div>'

def initials(name):
    return "".join(w[0] for w in name.replace("(", "").split() if w[0].isupper())[:2]
def stu_avatar(p):
    key = p.get("photo")
    if key and IMG.get("head_" + key):
        return f'<img class="avatar lg round" src="data:image/png;base64,{IMG["head_" + key]}" alt="{esc(p["name"])}" width="360" height="360">'
    return f'<span class="avatar mono lg round" aria-hidden="true">{esc(initials(p["name"]))}</span>'
def student_card(st):
    links = ([f'<a href="{esc(st["linkedin"])}">LinkedIn</a>'] if st.get("linkedin") and not LINKEDIN.get(st["name"]) else []) + id_links(st["name"])
    fig = ''
    if st.get("fig") and IMG.get(st["fig"]):
        fig = f'<figure class="stufig"><img src="data:image/jpeg;base64,{IMG[st["fig"]]}" alt="{esc(st.get("figcap", "Research figure"))}" loading="lazy"><figcaption>{esc(st.get("figcap", ""))}</figcaption></figure>'
    elif st.get("figsvg") and STUDENT_FIGS.get(st["figsvg"]):
        fig = f'<figure class="stufig"><div class="svgfig" role="img" aria-label="{esc(st.get("figcap", "Research figure"))}">{STUDENT_FIGS[st["figsvg"]]}</div><figcaption>{esc(st.get("figcap", ""))}</figcaption></figure>'
    return (f'<article class="stu">{stu_avatar(st)}'
            f'<h3>{esc(st["name"])}</h3><p class="ptitle">{esc(st["status"])}</p><p class="focus">{esc(st["focus"])}</p>'
            + student_highlight(st["name"])
            + '<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in links) + '</p>'
            + (f'<p class="gsline">{scholar_line(st["name"])}</p>' if scholar_line(st["name"]) else '')
            + metrics_slot({"name": st["name"]}) + fig + '</article>')
def alum_feature(a):
    links = ([f'<a href="{esc(a["linkedin"])}">LinkedIn</a>'] if a.get("linkedin") and not LINKEDIN.get(a["name"]) else []) + id_links(a["name"])
    inst = "Southern Illinois" if a["org"].startswith("Southern") else "Montana"
    return (f'<article class="stu feat">{stu_avatar(a)}'
            f'<h3>{esc(a["name"])} <span class="ptag">{esc(a["degree"])}</span></h3><p class="ptitle"><b>{esc(a["role"])}</b>, {esc(a["org"])}</p>'
            f'<p class="focus">{esc(a["focus"])}</p>' + student_highlight(a["name"])
            + '<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in links) + '</p>'
            + metrics_slot({"name": a["name"], "inst": inst}) + '</article>')

# ---------------------------------------------------------------- sponsors
# Drop official logo files into a "logos" folder next to this script, named by key
# (nsf.svg, doe.png, redhat.svg ...). SVG, PNG, or JPG. Tiles fall back to a typeset name.
SPONSORS = {
    "Federal sponsors": [
        {"key": "nsf", "name": "U.S. National Science Foundation", "url": "https://www.nsf.gov", "note": "SUMMIT (MRI Track 2, Award #2511635) and CAREER awards"},
        {"key": "doe", "name": "U.S. Department of Energy", "url": "https://www.energy.gov", "note": "CyberCARED cybersecurity center for energy delivery"},
        {"key": "onr", "name": "Office of Naval Research", "url": "https://www.onr.navy.mil", "note": "Department of the Navy. Post-disaster restoration of cyber-physical distribution grids"},
        {"key": "army", "name": "U.S. Army", "url": "https://www.army.mil", "note": "ARPO autonomous robotic planning and optimization"},
        {"key": "airforce", "name": "U.S. Air Force", "url": "https://www.af.mil", "note": "Command and control display equipment requirements"},
        {"key": "justice", "name": "National Institute of Justice", "url": "https://nij.ojp.gov", "note": "Information sharing for sex offender registration and notification"},
        {"key": "usmc", "name": "U.S. Marine Corps", "url": "https://www.marines.mil", "note": "MASCOT manycast architecture for tactical operations"},
    ],
    "State, international, and industry sponsors": [
        {"key": "mass", "name": "Commonwealth of Massachusetts", "url": "https://www.mass.gov", "note": "Advanced Nuclear and Fusion Energy Roadmaps, Healey-Driscoll Administration"},
        {"key": "iaea", "name": "International Atomic Energy Agency", "url": "https://www.iaea.org", "note": "Intercontinental Nuclear Institute training program"},
        {"key": "masstech", "name": "Massachusetts Technology Collaborative", "url": "https://masstech.org", "note": "ARPO-Sensor Fusion, Applied AI Models program"},
        {"key": "redhat", "name": "Red Hat", "url": "https://www.redhat.com", "note": "Open-source research: Friendly Fedora and Podman"},
        {"key": "navia", "name": "Navia Energy", "url": "https://naviaenergy.com", "note": "Resilient smart grids"},
    ],
    "Partner institutions": [
        {"key": "nyu", "name": "NYU Tandon School of Engineering", "url": "https://engineering.nyu.edu", "note": "SUMMIT federation site; Yuzhang Lin, Co-PI"},
        {"key": "wvu", "name": "West Virginia University", "url": "https://www.wvu.edu", "note": "SUMMIT federation site; Anurag Srivastava"},
        {"key": "umlarc", "name": "UMass Lowell Applied Research Corporation", "url": "", "note": "Place of performance for the ARPO projects"},
    ],
}
# --- overlay: NSF awards found by refresh.py that are not in the curated ledger
_auto_grants = _load_overlay("grants_auto.json", {"awards": []})
def _fmt_amt(v):
    try: v = float(v)
    except (TypeError, ValueError): return ""
    return f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1e3:.0f}K"
def _fmt_period(a, b):
    def f(d):
        try: return datetime.datetime.strptime(d, "%m/%d/%Y").strftime("%b %Y")
        except Exception: return ""
    return " to ".join(x for x in (f(a), f(b)) if x)
_CORE_SURNAMES = {"vokkarane", "aghara", "arias", "evans", "lin", "luo", "robinette", "son", "tseng", "xie"}
def _surname(name):
    name = re.sub(r"\(.*?\)", "", name or "").strip()
    if "," in name: name = name.split(",")[0]          # "Luo, Yan"
    return (name.split() or [""])[-1].strip(".").lower() if "," not in (name or "") else name.strip().lower()
_curated_ids = set(re.findall(r"#(\d{7})", " ".join(p.get("sponsor", "") + " " + p.get("title", "") for p in PROJECTS)))
from uml_roster import roster_match, split_name, is_uml
for a in _auto_grants.get("awards", []):
    if str(a.get("id", "")) in _curated_ids: continue
    # the same checks the pull applies: exactly UMass Lowell, and a roster person by full name.
    # Entries from the old surname-only pull carry no awardee field and are dropped here.
    if not is_uml(a.get("awardee")): continue
    _pi_person = roster_match(*split_name(a.get("pi", "")))
    _co_people = [p for p in (roster_match(*split_name(c)) for c in (a.get("copis") or [])) if p]
    if not _pi_person and not _co_people: continue
    a = dict(a, roster_person=_pi_person or _co_people[0], role="PI" if _pi_person else "Co-PI")
    end_ok = True
    try: end_ok = datetime.datetime.strptime(a.get("end", ""), "%m/%d/%Y").date() >= datetime.date.today() - datetime.timedelta(days=365)
    except Exception: pass
    if not end_ok: continue
    PROJECTS.append({"tag": "New" if a.get("found", "") >= (datetime.date.today() - datetime.timedelta(days=120)).isoformat() else "Active",
                     "role": a["role"], "lead_person": a["roster_person"],
                     "url": a.get("url", ""), "link": "NIH RePORTER record" if a.get("source") == "NIH" else "",
                     "sponsor": ((f"National Institutes of Health, {a['program']} (Project {a['id'][4:]})") if a.get("source") == "NIH" else
                                 ("National Science Foundation" + (f", {a['program']}" if a.get("program") else "") + f" (Award #{a['id']})")),
                     "title": a["title"], "amount": _fmt_amt(a.get("amount")), "period": _fmt_period(a.get("start"), a.get("end")),
                     "team": "PI " + a.get("pi", "") + ("; Co-PIs " + ", ".join(a["copis"]) if a.get("copis") else ""),
                     "desc": f"From the {'NIH RePORTER' if a.get('source') == 'NIH' else 'NSF Awards'} database, verified as a UMass Lowell award with a center member as " + a["role"] + ".",
                     "domain": "NIH" if a.get("source") == "NIH" else "NSF"})


# --- Yan Luo's awards active since the center's founding (Sept. 2019), from his CV (Sept. 2026).
# Amounts are award face value as listed there.
PROJECTS += [
    {"tag": "Active", "sponsor": "National Science Foundation, PFI-RP (Award #2329826)", "role": "PI",
     "title": "BioSPACE: Biosensing Surveillance of Pathogens in Aquaculture and Coastal Environments",
     "amount": "$1.0M", "period": "Sept 2023 to Aug 2027", "team": "PI Yan Luo; Co-PIs Sheree Pagsuyoin, Frederic Chain, J. Jayapalan",
     "desc": "Partnership for Innovation project on sensing and surveillance of pathogens in aquaculture and coastal waters.", "domain": "Sensing"},
    {"tag": "Active", "sponsor": "National Institutes of Health", "role": "Co-PI",
     "title": "Unsupervised Deep PCCT Reconstruction for Human Extremity Imaging",
     "amount": "$2.30M", "period": "July 2023 to Apr 2027", "team": "PI Hengyong Yu; Co-PIs Yan Luo, Yu Cao",
     "desc": "Deep learning reconstruction for photon-counting CT imaging of human extremities.", "domain": "Health"},
    {"tag": "Active", "sponsor": "National Institutes of Health", "role": "Co-PI",
     "title": "AI-based Cardiac CT",
     "amount": "$2.4M", "period": "May 2023 to Feb 2027", "team": "PI Hengyong Yu; Co-PIs Yan Luo, Yu Cao",
     "desc": "Artificial intelligence methods for cardiac computed tomography.", "domain": "Health"},
    {"tag": "Completed", "sponsor": "National Offshore Wind R&D Consortium", "role": "Co-PI",
     "title": "A Novel Structural Health Monitoring System for Offshore Wind Turbines",
     "amount": "$800K", "period": "Feb 2023 to Dec 2025", "team": "PI Murat Inalpolat; Co-PIs Christopher Niezrecki, Yan Luo",
     "desc": "Structural health monitoring for offshore wind turbines.", "domain": "Energy"},
    {"tag": "Completed", "sponsor": "Trinity Foundation", "role": "Co-PI",
     "title": "Disease Surveillance with Multi-modal Sensor Network and Data Analytics",
     "amount": "$660K", "period": "Oct 2021 to Mar 2026", "team": "PI Sheree Pagsuyoin; Co-PIs Yan Luo, Frederic Chain",
     "desc": "Disease surveillance built on a multi-modal sensor network and data analytics.", "domain": "Health"},
    {"tag": "Completed", "sponsor": "National Science Foundation, MRI (Award #2018992)", "role": "Co-PI",
     "title": "MRI: Development of a Calibration System for Stereophotogrammetry to Enable Large-Scale Measurement and Monitoring",
     "amount": "$455K", "period": "Sept 2020 to Aug 2023", "team": "PI Alessandro Sabato; Co-PIs Christopher Niezrecki, Yan Luo, Kshitij Jerath",
     "desc": "Instrument development for calibrating stereophotogrammetry in large-scale structural measurement.", "domain": "Sensing"},
    {"tag": "Completed", "sponsor": "U.S. Department of Energy", "role": "Co-PI",
     "title": "Development of an Acoustics-based Automated Offshore Wind Turbine Blade Structural Health Monitoring System",
     "amount": "$1.4M", "period": "Sept 2020 to Aug 2023", "team": "PI Murat Inalpolat; Co-PIs Christopher Niezrecki, Yan Luo",
     "desc": "Acoustic sensing to monitor offshore wind turbine blades automatically.", "domain": "Energy"},
    {"tag": "Completed", "sponsor": "National Science Foundation (Award #1916374)", "role": "Co-PI",
     "title": "Collaborative Research: A Low-Cost, Digital Biosensing Platform with Single Protein Biomarker Sensitivity",
     "amount": "$225K", "period": "Sept 2019 to Aug 2023", "team": "PI Hongwei Sun; Co-PI Yan Luo",
     "desc": "A low-cost biosensing platform sensitive to single protein biomarkers.", "domain": "Health"},
    {"tag": "Completed", "sponsor": "National Science Foundation, CICI (Award #1738965)", "role": "PI",
     "title": "CICI: RSARC: SECTOR: Building a Secure and Compliant Cyberinfrastructure for Translational Research",
     "amount": "$1.0M", "period": "Sept 2017 to Aug 2022", "team": "PI Yan Luo; Co-PIs Yu Cao, Peilong Li, Silvia Corvera, Jomol Mathew",
     "desc": "Secure, regulation-compliant cyberinfrastructure for translational health research.", "domain": "Health"},
    {"tag": "Completed", "sponsor": "National Science Foundation, CICI (Award #1547428)", "role": "PI",
     "title": "CICI: Secure Data Architecture: STREAMS: Secure Transport and Research Architecture for Monitoring Stroke Recovery",
     "amount": "$500K", "period": "Jan 2016 to Dec 2020", "team": "PI Yan Luo; Co-PIs Yu Cao, Xinwen Fu, Martin Margala",
     "desc": "Secure data transport and architecture for monitoring stroke recovery.", "domain": "Health"},
    {"tag": "Completed", "sponsor": "National Science Foundation, IRNC (Award #1450996)", "role": "Lead PI",
     "title": "IRNC: AMI: Collaborative Research: Software-Defined and Privacy-Preserving Network Measurement Instrument and Services for Understanding Data-Driven Science Discovery",
     "amount": "$1.25M", "share": "$2.35M across four institutions", "period": "Apr 2015 to Mar 2020", "team": "Lead PI Yan Luo",
     "desc": "Network measurement instrument and services for international research networks, with the University of Kentucky, UMass Boston, and UTEP.", "domain": "Networks"},
]

# --- The director's earlier external awards, from the CV (Sept. 2026). Amounts are award face value;
# where UMass Lowell held a share of a consortium award, the share is noted.
PROJECTS += [
    {"tag": "Completed", "sponsor": "NSF CC*DNI", "role": "PI",
     "title": "Network Cyberinfrastructure for Biomedical Informatics Innovation",
     "amount": "$1.02M", "period": "2015 to 2019", "team": "PI Vinod Vokkarane; Co-PIs Yan Luo and Yu Cao",
     "desc": "Campus cyberinfrastructure to move and analyze large biomedical data sets at UMass Lowell.", "domain": "Networks"},
    {"tag": "Completed", "sponsor": "National Institute of Justice", "role": "Co-PI",
     "title": "Information Sharing and Its Effect on Tracking Sex Offenders and Community Awareness (SORNA)",
     "amount": "$1M", "period": "2015 to 2019", "team": "Co-PI Vinod Vokkarane; Lead PI Andrew Harris (UMass Lowell)",
     "desc": "Information sharing architecture and analysis for sex offender registration and notification systems.", "domain": "Data systems"},
    {"tag": "Completed", "sponsor": "U.S. Air Force", "role": "Co-PI",
     "title": "Command and Control Display Equipment (CCDE) Requirements Specification",
     "amount": "$865K", "period": "2017 to 2018", "team": "Co-PI Vinod Vokkarane; Lead PI Kavitha Chandra (UMass Lowell)",
     "desc": "Requirements analysis and specification for command and control display equipment.", "domain": "Defense"},
    {"tag": "Completed", "sponsor": "U.S. Department of Energy, ASCR", "role": "PI",
     "title": "PROPER: Parallel Resource-Optimized Provisioning of End-to-End Requests",
     "amount": "$401K", "period": "2014 to 2018", "team": "PI Vinod Vokkarane",
     "desc": "Provisioning algorithms for end-to-end circuits across Department of Energy science networks.", "domain": "Networks"},
    {"tag": "Completed", "sponsor": "NSF CC*IIE", "role": "Co-PI",
     "title": "FLowell: Accelerating Data-Driven Scientific Research at UMass Lowell",
     "amount": "$500K", "period": "2014 to 2017", "team": "Co-PI Vinod Vokkarane; Lead PI Yan Luo (UMass Lowell)",
     "desc": "Campus science network upgrade for data-intensive research across the university.", "domain": "Networks"},
    {"tag": "Completed", "sponsor": "NSF NeTS Small", "role": "PI",
     "title": "CARGONET: Coordinated Advance Reservation for Grid over Optical Networks",
     "amount": "$325K", "share": "plus a $40K REU supplement", "period": "2012 to 2017", "team": "PI Vinod Vokkarane",
     "desc": "Advance reservation of optical circuits for grid and data-intensive science workflows.", "domain": "Networks"},
    {"tag": "Completed", "sponsor": "NSF CSR Small", "role": "Co-PI",
     "title": "Bridging Reliability Analysis and Reality in Sensor Systems: Theories and Applications",
     "amount": "$441K", "share": "UMass share $278K", "period": "2011 to 2015",
     "team": "Co-PI Vinod Vokkarane; Lead PI Liudong Xing (UMass Dartmouth), with Yan Sun (URI)",
     "desc": "Reliability and fault tolerance models for wireless sensor systems.", "domain": "Sensing"},
    {"tag": "Completed", "sponsor": "U.S. Department of Energy, Office of Science", "role": "PI",
     "title": "COMMON: Coordinated Multi-Layer Multi-Domain Optical Network",
     "amount": "$525K", "period": "2010 to 2013", "team": "PI Vinod Vokkarane",
     "desc": "Coordinated provisioning across layers and administrative domains in optical networks.", "domain": "Networks"},
    {"tag": "Completed", "sponsor": "U.S. Marine Corps", "role": "PI",
     "title": "MASCOT: Manycast Architecture for Service-Oriented Tactical Operations",
     "amount": "$50K", "period": "2008", "team": "PI Vinod Vokkarane",
     "desc": "Manycast communication architecture for service-oriented tactical networks.", "domain": "Defense"},
    {"tag": "Completed", "sponsor": "NSF NeTS Small", "role": "PI",
     "title": "SOON: Service-Oriented Optical Networks",
     "amount": "$476K", "share": "UMass share $240K", "period": "2006 to 2011",
     "team": "PI Vinod Vokkarane, with Jason Jue (UT Dallas)",
     "desc": "Service-oriented architectures for provisioning in optical networks.", "domain": "Networks"},
    {"tag": "Completed", "sponsor": "NSF CCLI", "role": "PI",
     "title": "NET-SEAL: Teaching Computer Networks Through Simulation Experiments and Animation Library",
     "amount": "$168K", "share": "UMass share $127K", "period": "2006 to 2010", "team": "PI Vinod Vokkarane",
     "desc": "Simulation experiments and an animation library for teaching computer networking.", "domain": "Education"},
]

LOGOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos")
_MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
def logo_src(key):
    for ext, mime in _MIME.items():
        p = os.path.join(LOGOS_DIR, key + ext)
        if os.path.exists(p):
            import base64
            return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
    return ""
def logo_tile(sp):
    src = logo_src(sp["key"])
    mark = f'<img src="{src}" alt="{esc(sp["name"])} logo">' if src else f'<span class="wm">{esc(sp["name"])}</span>'
    inner = f'<div class="mark">{mark}</div><div class="note">{esc(sp["note"])}</div>'
    if sp.get("url"):
        return f'<a class="logo-tile" href="{esc(sp["url"])}" title="{esc(sp["name"])}">{inner}</a>'
    return f'<div class="logo-tile">{inner}</div>'



STUDENT_FIGS = {
"ayush": """<svg viewBox="30 50 740 530" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" stroke-linejoin="round" font-family="IBM Plex Sans, Arial, sans-serif">
<rect x="0" y="0" width="800" height="600" fill="#fff"/>
<!-- transmission grid -->
<g stroke="#044978" stroke-width="3">
  <path d="M80 470l30-230h30l30 230M100 400h70M108 340h54M116 280h38M64 400h102M72 340h90M84 280h70"/>
  <path d="M640 470l30-230h30l30 230M660 400h70M668 340h54M676 280h38M624 400h102M632 340h90M644 280h70"/>
</g>
<path d="M116 280Q400 400 676 280M84 340Q400 470 644 340" stroke="#D5DCE5" stroke-width="4"/>
<path d="M116 280Q400 400 676 280" stroke="#0A777F" stroke-width="5" stroke-dasharray="10 18"/>
<path d="M84 340Q400 470 644 340" stroke="#0A777F" stroke-width="5" stroke-dasharray="10 18"/>
<!-- substation with controller -->
<rect x="330" y="420" width="140" height="60" rx="8" fill="#044978"/>
<g stroke="#fff" stroke-width="2" opacity=".7"><path d="M360 428v44M390 428v44M420 428v44M450 428v44M330 450h140"/></g>
<rect x="352" y="380" width="96" height="30" rx="6" fill="#fff" stroke="#044978" stroke-width="3"/>
<text x="400" y="401" text-anchor="middle" font-size="16" fill="#044978" font-weight="600">controller</text>
<!-- AI detector -->
<rect x="290" y="70" width="220" height="160" rx="16" fill="#F3F7FA" stroke="#044978" stroke-width="3"/>
<g fill="#044978"><circle cx="330" cy="110" r="9"/><circle cx="330" cy="150" r="9"/><circle cx="330" cy="190" r="9"/><circle cx="400" cy="90" r="9"/><circle cx="400" cy="130" r="9"/><circle cx="400" cy="170" r="9"/><circle cx="400" cy="210" r="9"/></g>
<g fill="#0A777F"><circle cx="470" cy="130" r="10"/><circle cx="470" cy="170" r="10"/></g>
<g stroke="#9AB0C4" stroke-width="1.5"><path d="M339 110L391 90M339 110L391 130M339 150L391 130M339 150L391 170M339 190L391 170M339 190L391 210M409 90L461 130M409 130L461 130M409 170L461 170M409 210L461 170M409 130L461 170M409 170L461 130"/></g>
<text x="400" y="255" text-anchor="middle" font-size="16" fill="#5B6B82">anomaly and intrusion detection</text>
<!-- telemetry up, decisions down -->
<path d="M380 380V235" stroke="#0A777F" stroke-width="4" stroke-dasharray="8 12"/>
<path d="M420 235V380" stroke="#3BA995" stroke-width="4" stroke-dasharray="8 12"/>
<path d="M373 250l7-14 7 14M413 366l7 14 7-14" stroke="#0A777F" stroke-width="3"/>
<text x="352" y="312" text-anchor="end" font-size="15" fill="#5B6B82">telemetry</text>
<text x="448" y="312" font-size="15" fill="#5B6B82">control</text>
<!-- shield -->
<path d="M560 260l40 14v34c0 28-17 46-40 56-23-10-40-28-40-56v-34z" fill="#3BA995"/>
<path d="M542 302l12 12 26-28" stroke="#fff" stroke-width="6"/>
<!-- attacker -->
<g stroke="#E25555" stroke-width="4"><path d="M700 150l-40 26 20 6-26 34"/></g>
<circle cx="654" cy="216" r="7" fill="#E25555"/>
<path d="M640 226l-60 40" stroke="#E25555" stroke-width="3" stroke-dasharray="6 8"/>
<text x="640" y="130" text-anchor="middle" font-size="15" fill="#E25555">false data injection</text>
<path d="M40 500h720" stroke="#D5DCE5" stroke-width="3"/>
<text x="400" y="560" text-anchor="middle" font-size="18" fill="#0E2036" font-weight="600">AI-based defense of a cyber-physical power grid</text>
</svg>""",
"suvhasis": """<svg viewBox="30 80 740 500" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" stroke-linejoin="round" font-family="IBM Plex Sans, Arial, sans-serif">
<rect x="0" y="0" width="800" height="600" fill="#fff"/>
<!-- fiber link with amplifiers -->
<g stroke="#044978" stroke-width="4"><path d="M60 140H740"/></g>
<g fill="#fff" stroke="#044978" stroke-width="3"><path d="M200 120l40 20-40 20zM430 120l40 20-40 20zM660 120l40 20-40 20z"/></g>
<g fill="#0A777F"><circle cx="60" cy="140" r="12"/><circle cx="740" cy="140" r="12"/></g>
<text x="60" y="180" text-anchor="start" font-size="15" fill="#5B6B82" transform="translate(-40,0)">transmitter</text>
<text x="740" y="180" text-anchor="middle" font-size="15" fill="#5B6B82">receiver</text>
<text x="450" y="105" text-anchor="middle" font-size="15" fill="#5B6B82">amplified spans</text>
<!-- flex-grid spectrum -->
<path d="M100 400H700" stroke="#5B6B82" stroke-width="2"/>
<g stroke="#D5DCE5" stroke-width="1.5"><path d="M100 400V250M700 400V250"/></g>
<g stroke="none">
  <rect x="112" y="300" width="60" height="100" fill="#044978"/><rect x="180" y="330" width="40" height="70" fill="#0A777F"/><rect x="228" y="270" width="100" height="130" fill="#044978"/>
  <rect x="336" y="345" width="40" height="55" fill="#3BA995"/><rect x="384" y="290" width="80" height="110" fill="#0A777F"/><rect x="472" y="320" width="60" height="80" fill="#3BA995"/>
  <rect x="540" y="260" width="120" height="140" fill="#044978"/>
</g>
<!-- impairment noise floor rising with load -->
<path d="M100 385C220 380 330 372 460 360S620 345 700 330" stroke="#E25555" stroke-width="3" stroke-dasharray="7 9"/>
<text x="700" y="318" text-anchor="end" font-size="14" fill="#E25555">nonlinear interference</text>
<g font-size="14" fill="#5B6B82" text-anchor="middle"><text x="142" y="420">16QAM</text><text x="278" y="420">8QAM</text><text x="424" y="420">QPSK</text><text x="600" y="420">64QAM</text></g>
<text x="400" y="452" text-anchor="middle" font-size="15" fill="#5B6B82">flexible grid: spectrum, modulation, and power chosen per lightpath</text>
<!-- constellation inset -->
<rect x="590" y="200" width="150" height="40" rx="6" fill="#F3F7FA" stroke="#D5DCE5"/>
<g fill="#0A777F"><circle cx="612" cy="212" r="3"/><circle cx="628" cy="212" r="3"/><circle cx="644" cy="212" r="3"/><circle cx="660" cy="212" r="3"/><circle cx="612" cy="228" r="3"/><circle cx="628" cy="228" r="3"/><circle cx="644" cy="228" r="3"/><circle cx="660" cy="228" r="3"/></g>
<text x="705" y="225" text-anchor="middle" font-size="12" fill="#5B6B82">QoT</text>
<text x="400" y="560" text-anchor="middle" font-size="18" fill="#0E2036" font-weight="600">Impairment-aware elastic optical networking</text>
</svg>""",
}



# ---------------------------------------------------------------- project filters
# Each project row carries three data attributes so the ledger can be filtered. All three are derived
# from fields the row already has, so a new award needs no extra tagging.
_DOMAIN_THRUST = {
    "Energy": "grid", "Networks": "fiber", "Autonomy": "ai", "Distributed systems": "edge",
    "HPC": "hpc", "Printed electronics": "chip", "Transportation": "health", "Education": "health",
    "Nuclear": "nuclear", "Data systems": "ai", "Defense": "fiber", "Sensing": "chip", "NIH": "health",
}
_NAME = r"([A-Z][a-zA-Z'-]+(?:\s+(?:[A-Z]\.|[A-Z][a-zA-Z'-]+)){1,2})"
def _roster():
    out = {}
    for grp in ("director", "core", "affiliated", "external"):
        for p in ([FACULTY[grp]] if grp == "director" else FACULTY[grp]):
            full = re.sub(r"\s*\(.*?\)", "", p["name"]).strip()
            out[full.split()[-1].lower()] = full
    return out

def canonical_person(name):
    """Map any spelling of a name to the roster's form of it; unknown people come back unchanged."""
    if not name: return ""
    n = re.sub(r"\s*\(.*?\)", "", name).strip()
    sur = (n.split(",")[0] if "," in n else (n.split() or [""])[-1]).strip(".").lower()
    return _roster().get(sur, n.title() if n.isupper() else n)

def _project_pi_raw(pr):
    """The lead investigator, from the team line. Handles PI, UMass Lowell PI, Lead, Co-director, and
    three-part names, falling back to the first Co-PI when no lead is named."""
    team = pr.get("team", "")
    for pat in (r"(?:^|; )(?:UMass Lowell )?PI " + _NAME,
                r"(?:^|; )Lead: " + _NAME,
                r"(?:^|; )Co-director: " + _NAME,
                r"(?:^|; )Co-PIs? " + _NAME):
        m = re.search(pat, team)
        if m: return re.sub(r"\s+", " ", m.group(1)).strip()
    return ""

def project_pi(pr):
    if pr.get("lead_person"): return canonical_person(pr["lead_person"])
    return canonical_person(_project_pi_raw(pr))

_ROLE_SEG = [(r"^Lead PI\s+(.*)$", "Lead PI"), (r"^(?:UMass Lowell )?PI\s+(.*)$", "PI"), (r"^Lead:\s+(.*)$", "Lead"),
             (r"^Co-director:\s+(.*)$", "Co-director"), (r"^Co-PIs?\s+(.*)$", "Co-PI")]
def project_people(pr):
    """Every investigator named on the team line, as (roster name, role) in the order written: PI, UMass
    Lowell PI, Lead PI, Lead, Co-director, and Co-PIs. Senior personnel, 'with ...' collaborators, and
    performing sites are not investigators and are left out. Names are mapped to the roster's spelling."""
    out, seen = [], set()
    for seg in re.split(r";\s*", pr.get("team", "")):
        seg = seg.strip()
        for pat, role in _ROLE_SEG:
            m = re.match(pat, seg)
            if not m: continue
            names = re.split(r",\s*with\s+|\s+with\s+", m.group(1), 1)[0]      # "Lead: X, with the Rist Institute"
            names = re.sub(r"\s*\([^)]*\)", "", names)                             # "(NYU)", "(Director, RURI and PERC)"
            for n in re.split(r",\s*|\s+and\s+", names):
                n = n.strip(" .")
                if not re.fullmatch(_NAME, n): continue
                name = canonical_person(n)
                if name not in seen:
                    seen.add(name); out.append((name, role))
            break
    return out

def project_years(pr):
    """Every calendar year the award touches, so a filter on 2026 finds awards running through it."""
    yrs = [int(y) for y in re.findall(r"(20\d\d)", pr.get("period", ""))]
    if not yrs: return []
    return list(range(min(yrs), max(yrs) + 1))

_LEAD_THRUST = {"Vokkarane": "grid", "Lin": "grid", "Luo": "ai", "Tseng": "edge", "Arias": "chip",
                "Son": "hpc", "Xie": "health", "Robinette": "health", "Aghara": "nuclear", "Akyurtlu": "chip"}
def project_thrust(pr):
    t = _DOMAIN_THRUST.get(pr.get("domain", ""), "")
    if t: return t
    return _LEAD_THRUST.get(project_pi(pr).split()[-1] if project_pi(pr) else "", "")

# ---------------------------------------------------------------- laboratories and facilities
# Each entry: the lab, who runs it, what it studies, and what it can offer a collaborator.
LABS = [
    {"name": "Advanced Communication Networks Laboratory (ACNL)", "lead": "Vinod M. Vokkarane",
     "dept": "Electrical and Computer Engineering",
     "what": "The director's group, working on optical and 6G transport, smart grid cybersecurity, and the AI that runs both. Doctoral students here build and test on real instruments and real data rather than on paper alone.",
     "offers": ["Multi-band and space-division multiplexed optical network simulation",
                "Grid intrusion detection and federated anomaly detection",
                "Reproducible benchmarking through the open-source FUSION framework",
                "The NATIG cyber-physical co-simulation testbed (HELICS, GridLAB-D, ns-3)"],
     "links": [("Lab website", "acnl/index.html"), ("Research record, 2002 to 2026", "acnl.html"), ("Students in the group", "students.html"), ("FUSION on GitHub", "https://github.com/SDNNetSim/FUSION")],
     "art": "acnl"},
    {"name": "SUMMIT federated smart grid testbed", "lead": "Vinod M. Vokkarane, with Arias, Tseng, Lin, and Srivastava",
     "dept": "NSF Major Research Instrumentation, Track 2",
     "what": "A three-site instrument linking real-time power system simulation with control, networking, and cybersecurity hardware in the loop across UMass Lowell, NYU Tandon, and West Virginia University, delivered to collaborators as hardware-in-the-loop Simulation-as-a-Service.",
     "offers": ["RTDS real-time digital simulation of the Northeast transmission grid",
                "Network emulation for latency, loss, and attack scenarios",
                "Optical, RF, and FPGA equipment for transport and edge layers",
                "Wide-area software-defined networking between the three sites"],
     "links": [("SUMMIT project page", "summit.html")],
     "art": "summit"},
    {"name": "Integrated Nuclear Security and Safeguards Laboratory (INSSL)", "lead": "Sukesh Aghara",
     "dept": "Chemical (Nuclear) Engineering",
     "what": "Research, education, and training tools for global nuclear security and safeguards, alongside the UMass Lowell research reactor. The lab has radiation detectors and cyber-physical testbeds, and its work on nuclear facility cybersecurity, safeguards verification, and advanced reactor modeling is supported by federal agencies including NNSA.",
     "offers": ["Safeguards measurement and detector response modeling",
                "Security of nuclear facilities and robotic platforms for hazardous environments",
                "Training through the IAEA-funded Intercontinental Nuclear Institute"],
     "links": [("INSSL", "https://www.uml.edu/Research/INSSL/")],
     "art": "inssl"},
    {"name": "Printed Electronics Research Collaborative (PERC) and the Raytheon UMass Lowell Research Institute (RURI)",
     "lead": "Alkim Akyurtlu, with Oshadha Ranasingha", "dept": "Electrical and Computer Engineering",
     "what": "Additive manufacturing and printed electronics for RF and microwave devices, wearables, and functional printable inks, with RURI as the industry-facing research institute.",
     "offers": ["Aerosol-jet and inkjet printing of functional materials",
                "RF and microwave device characterization",
                "Fully printed micro-supercapacitors and energy harvesting devices",
                "Hardware authentication for printed and flexible devices"],
     "links": [("PERC", "https://www.uml.edu/research/perc/"), ("RURI", "https://www.uml.edu/Research/PERC/RURI/")],
     "art": "perc"},
    {"name": "Lowell Center for Space Science and Technology (LoCSST)", "lead": "Supriya Chakrabarti",
     "dept": "Physics and Applied Physics",
     "what": "Space experiments and instrumentation, from hyperspectral imaging across the ultraviolet to the near infrared through lidar and exoplanet observation.",
     "offers": ["Optical instrument design, build, and calibration",
                "Balloon and sounding-rocket payload development",
                "Hyperspectral imaging and lidar systems"],
     "links": [("LoCSST", "https://www.uml.edu/research/locsst/")],
     "art": "locsst"},
    {"name": "UMass Center for Digital Health", "lead": "Yu Cao",
     "dept": "Miner School of Computer and Information Sciences",
     "what": "A multi-campus partnership across Lowell, Worcester, and Boston working on digital health innovation, from medical imaging to platforms that move clinical data safely.",
     "offers": ["Medical imaging and multimodal deep learning",
                "Validation and evaluation of digital health tools",
                "Clinical data platforms and academic-industry partnership"],
     "links": [("Center for Digital Health", "https://www.uml.edu/research/digital-health/")],
     "art": "cdh"},
    {"name": "Center for Energy Innovation and the Rist Institute for Sustainability and Energy",
     "lead": "Christopher Niezrecki, with Murat Inalpolat", "dept": "Mechanical and Industrial Engineering",
     "what": "Renewable energy systems and structural health monitoring: wind turbine dynamics, inspection of blades and bridges, and the sensing that keeps large structures safe.",
     "offers": ["Structural dynamics, vibration, and acoustic testing",
                "Wind turbine blade inspection, including drone-based methods",
                "Structural health monitoring for bridges and buildings"],
     "links": [("Center for Energy Innovation", "https://www.uml.edu/research/energy/"), ("Rist Institute", "https://www.uml.edu/sustainability/")],
     "art": "cei"},
]


# ---------------------------------------------------------------- journal metrics
# journals.json maps a journal name (exactly as it appears in the publication records) to its metrics:
#   {"IEEE Transactions on Smart Grid": {"if": 9.6, "if_year": 2024, "quartile": "Q1", "sjr": 3.1, "source": "JCR 2024"}}
# The Journal Impact Factor is Clarivate's and comes from Journal Citation Reports, which UMass Lowell
# licenses; enter it by hand from JCR. Quartile and SJR can be filled automatically from SCImago by
# refresh.py, which is open data. Any field may be left out and the chip shows what is there.
JOURNALS = {}
try:
    JOURNALS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "journals.json")))
except Exception:
    pass
def _jkey(name):
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower().replace("&amp;", "&")).strip()
_JLOOKUP = {_jkey(k): v for k, v in JOURNALS.items()}
def journal_chip(venue):
    m = _JLOOKUP.get(_jkey(venue))
    if not m: return ""
    bits = []
    if m.get("if"): bits.append(f'IF {m["if"]}' + (f' ({m["if_year"]})' if m.get("if_year") else ""))
    if m.get("quartile"): bits.append(str(m["quartile"]))
    if m.get("sjr"): bits.append(f'SJR {m["sjr"]}')
    if not bits: return ""
    return f'<span class="jm" title="{esc(m.get("source") or "journal metrics")}">' + " &middot; ".join(esc(b) for b in bits) + "</span>"


# ---------------------------------------------------------------- student publication highlights
# Papers are matched to a student by surname AND first initial AND the presence of their advisor on
# the paper, which is what keeps a common surname from collecting someone else's work. Everything
# here is computed from P; nothing is entered by hand.
STUDENT_ADVISOR = {
    "Arash Rezaee": ("Rezaee", "A", {"Vokkarane"}), "Ryan McCann": ("McCann", "R", {"Vokkarane"}),
    "Kenneth Patrick Watts": ("Watts", "K", {"Vokkarane"}), "Suvhasis Mukhopadhyay": ("Mukhopadhyay", "S", {"Vokkarane"}),
    "Mehran Sasaninia": ("Sasaninia", "M", {"Vokkarane"}), "Ayush Pandey": ("Pandey", "A", {"Vokkarane"}),
    "Md Zahidul Islam": ("Islam", "M", {"Lin", "Vokkarane"}), "Shamsun Nahar Edib": ("Edib", "S", {"Lin", "Vokkarane"}),
}
def pat_of(name):
    sur, ini, _ = STUDENT_ADVISOR[name]
    return re.compile(r"\b" + ini + r"\.\s*(?:[A-Z]\.\s*)?" + re.escape(sur) + r"\b")

def student_papers(name):
    spec = STUDENT_ADVISOR.get(name)
    if not spec: return []
    sur, ini, adv = spec
    pat = pat_of(name)
    out = [p for p in P if (set(p["faculty"]) & adv) and pat.search(", ".join(p["authors"]) if isinstance(p["authors"], list) else p["authors"])]
    return sorted(out, key=lambda p: (-p["year"], -(month_of(p) or 0)))

def student_highlight(name):
    """A one-line record plus the newest journal paper, for a student card."""
    papers = student_papers(name)
    if not papers: return ""
    j = [p for p in papers if p["type"] == "journal"]
    bits = []
    if j: bits.append(f'<b>{len(j)}</b> journal paper' + ("s" if len(j) != 1 else ""))
    other = len(papers) - len(j)
    if other: bits.append(f'<b>{other}</b> conference paper' + ("s" if other != 1 else ""))
    line = '<p class="stupubs">' + ", ".join(bits) + " with the center</p>"
    # prefer a paper the student led, so co-authors do not all show the same highlight
    def first_author(p):
        au = p["authors"][0] if isinstance(p["authors"], list) else p["authors"].split(",")[0]
        return pat_of(name).search(au) is not None
    lead = [p for p in j if first_author(p)] or [p for p in papers if first_author(p)]
    top = (lead or j or papers)[0]
    title = esc(top["title"])
    if top.get("doi"): title = f'<a href="https://doi.org/{esc(top["doi"])}">{title}</a>'
    line += (f'<p class="stupub"><span class="lbl">Selected paper</span>{title}'
             f'<span class="v"><i>{esc(top["venue"])}</i>, {esc(top["details"])}</span></p>')
    return line

# ---------------------------------------------------------------- researcher identifiers
SCHOLAR = {
    "Vinod M. Vokkarane": "EIIbTe8AAAAJ", "Lewis Tseng": "DP_DMPAAAAAJ", "Hengyong Yu": "wQcl7k8AAAAJ", "Yuanchang Xie": "5kXk7FEAAAAJ",
    "Christopher Niezrecki": "bdmF58cAAAAJ", "Yan Luo": "H3ifH2gAAAAJ", "Yu Cao": "97RDUygAAAAJ", "Murat Inalpolat": "khGOgZgAAAAJ",
    "Martin Margala": "ANcbeNIAAAAJ", "Yuzhang Lin": "AHw2wzUAAAAJ", "Seung Woo Son": "D9v08JgAAAAJ", "Sukesh Aghara": "tWlkv-kAAAAJ", "Paul Robinette": "izN2PKAAAAAJ", "Alkim Akyurtlu": "ixtU3E4AAAAJ",
    "Chunxiao (Tricia) Chigan": "qoo1Tc0AAAAJ",
    # Sent Sept. 2026 in this order: Arias, Chakrabarti, Evans, Ranasingha. Swap the IDs here if any
    # profile opens on the wrong person.
    "Orlando Arias": "LyL2zHwAAAAJ",
    # Corrected Sept. 2026 against each profile's own name: the IDs were shifted by one position.
    # Supriya Chakrabarti has no Scholar profile found; the site links a Scholar search for him instead.
    "Sheree A. Pagsuyoin": "CmHDkoIAAAAJ",
    "Md Zahidul Islam": "i_ebAeUAAAAJ", "Shamsun Nahar Edib": "xgysIYIAAAAJ", "Yue Wang": "fu07D-gAAAAJ", "Yan Cui": "nAVlj58AAAAJ", "Dylan A. P. Davis": "HL3j-7sAAAAJ", "Arash Deylamsalehi": "VobjklIAAAAJ", "Jeremy M. Plante": "oYnitXIAAAAJ", "Amir Ehsani Zonouz": "WUi_j6AAAAAJ", "Thilo Schöndienst": "7X5H3_YAAAAJ", "Juzi Zhao": "9RfENp0AAAAJ", "Arush Gadkar": "KOQPJJAAAAAJ", "Balagangadhar Bathula": "1c-DqjsAAAAJ", "Nicholas G. Evans": "N_0jmg8AAAAJ", "Oshadha Ranasingha": "-wPKnUAAAAAJ", "Anurag Srivastava": "_GtNYPMAAAAJ",
    # Current doctoral students, refreshed weekly with everyone above. To add one, use the name exactly as
    # written in STUDENTS and the user= part of the profile URL. Both checked Sept. 22, 2026: UMass Lowell
    # affiliation on the profile, and listed among the director's Scholar co-authors.
    "Arash Rezaee": "3OLFUJgAAAAJ", "Ryan McCann": "HPAbt0sAAAAJ",
    "Kenneth Patrick Watts": "3DaGyJoAAAAJ",   # sent by Ken, Sept. 25, 2026
}
ORCID = {
    "Vinod M. Vokkarane": "0000-0001-9205-2120", "Orlando Arias": "0009-0002-3948-5773", "Lewis Tseng": "0000-0002-4717-4038", "Seung Woo Son": "0000-0001-8922-418X",
    "Sukesh Aghara": "0000-0002-9419-2423", "Yuzhang Lin": "0000-0002-1366-4637", "Yan Luo": "0000-0002-5301-5092", "Yuanchang Xie": "0000-0002-0139-9362",
    "Yu Cao": "0000-0001-8624-1099", "Chunxiao (Tricia) Chigan": "0000-0002-0805-1932", "Murat Inalpolat": "0000-0002-2252-656X", "Paul Robinette": "0000-0001-8066-156X",
    "Hengyong Yu": "0000-0002-5852-0813", "Alkim Akyurtlu": "0000-0002-8222-9663", "Oshadha Ranasingha": "0000-0001-7399-0058",
    "Arash Rezaee": "0000-0002-8578-4347", "Ryan McCann": "0009-0003-4807-7963", "Md Zahidul Islam": "0000-0002-9980-6148", "Shamsun Nahar Edib": "0000-0002-9060-0936",
}
# Citation figures live in scholar.json, written by update_scholar.py (paste them off the profile pages)
# or by refresh.py when Google lets it read them. Every entry carries the date it was taken and the site
# prints that date, so a figure is never shown as fresher than it is.
SCHOLAR_DATA = {}
try:
    SCHOLAR_DATA = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scholar.json")))
except Exception:
    pass
LINKEDIN = {
    "Vinod M. Vokkarane": "https://www.linkedin.com/in/vinod-vokkarane-7656905/", "Lewis Tseng": "https://www.linkedin.com/in/lewis-tseng-a3164027/",
    "Yuanchang Xie": "https://www.linkedin.com/in/yuanchang-xie-38006b9/", "Hengyong Yu": "https://www.linkedin.com/in/hengyong-yu-72214a44/",
    "Seung Woo Son": "https://www.linkedin.com/in/seung-woo-son-uml/", "Yuzhang Lin": "https://www.linkedin.com/in/yuzhang-lin/",
    "Sukesh Aghara": "https://www.linkedin.com/in/sukeshaghara/",
}   # add the rest as "Name": "https://www.linkedin.com/in/..." and rebuild
POSTDOC_URL = "https://careers.pageuppeople.com/822/lowell/en-us/job/530223/postdoctoral-research-associate-vokkarane-lab-electrical-computer-engineering"
FUSION_URL = "https://github.com/SDNNetSim/FUSION"
for _n, _v in _load_overlay("scholar_auto.json", {}).items():
    if _v.get("citations") and _v.get("date", "") >= SCHOLAR_DATA.get(_n, {}).get("date", ""):
        SCHOLAR_DATA[_n] = _v
SCHOLAR_INST = {"Yuzhang Lin": "NYU", "Anurag Srivastava": "West Virginia University", "Md Zahidul Islam": "Southern Illinois University", "Shamsun Nahar Edib": "Montana State University"}
def id_links(name, inst="UMass Lowell"):
    out = []
    sid = SCHOLAR.get(name)
    # Only link a real profile. A profile search for someone without one lands on an empty results page.
    if sid: out.append(f'<a href="https://scholar.google.com/citations?user={esc(sid)}&amp;hl=en">Google Scholar</a>')
    if ORCID.get(name): out.append(f'<a href="https://orcid.org/{esc(ORCID[name])}">ORCID</a>')
    if LINKEDIN.get(name): out.append(f'<a href="{esc(LINKEDIN[name])}">LinkedIn</a>')
    return out
def scholar_line(name):
    d = SCHOLAR_DATA.get(name) or {}
    bits = []
    if d.get("citations"): bits.append(f'<b>{d["citations"]:,}</b> citations')
    if d.get("h"): bits.append(f'<b>{d["h"]}</b> h-index')
    if d.get("i10"): bits.append(f'<b>{d["i10"]}</b> i10-index')
    if not bits: return ""
    try:
        dt = datetime.datetime.strptime(d.get("date", ""), "%Y-%m-%d").date()
        when = dt.strftime("%b. %Y").replace("May.", "May")
        if (datetime.date.today() - dt).days > 190: when += ", not refreshed since"
    except Exception: when = ""
    return '<span class="gs">' + ", ".join(bits) + f' on Google Scholar{", " + when if when else ""}</span>'

# ---------------------------------------------------------------- themed SVG helpers
_COLOR_CLASS = {
    ("fill", "#044978"): "f-brand", ("stroke", "#044978"): "s-brand", ("fill", "#0A777F"): "f-sig", ("stroke", "#0A777F"): "s-sig",
    ("fill", "#3BA995"): "f-grn", ("stroke", "#3BA995"): "s-grn", ("fill", "#F3F7FA"): "f-tint", ("stroke", "#D5DCE5"): "s-line", ("fill", "#D5DCE5"): "f-line",
    ("fill", "#E25555"): "f-alert", ("stroke", "#E25555"): "s-alert", ("fill", "#FDECEC"): "f-alert-tint",
    ("stroke", "#0E2036"): "s-ink", ("fill", "#0E2036"): "f-ink",
    ("fill", "#fff"): "f-surface", ("fill", "#FFFFFF"): "f-surface", ("fill", "#ffffff"): "f-surface",
    ("fill", "#5B6B82"): "f-muted", ("stroke", "#5B6B82"): "s-muted", ("fill", "#2B4162"): "f-ink2",
    ("stroke", "#0E8FA3"): "s-sig", ("fill", "#0E8FA3"): "f-sig", ("fill", "#E3F3F6"): "f-sigt",
    ("stroke", "#E39A16"): "s-amb", ("fill", "#E39A16"): "f-amb",
}
_ATTR_RE = re.compile(r'\s(fill|stroke)="(#[0-9A-Fa-f]{3,6})"')

def theme_svg(svg):
    """Rewrite hard-coded fill/stroke colors into theme classes so the drawing follows light/dark mode."""
    def fix_tag(m):
        tag = m.group(0)
        classes = []
        def sub(am):
            key = (am.group(1), am.group(2))
            if key in _COLOR_CLASS:
                classes.append(_COLOR_CLASS[key]); return ""
            return am.group(0)
        tag = _ATTR_RE.sub(sub, tag)
        if classes:
            cm = re.search(r'\sclass="([^"]*)"', tag)
            if cm:
                tag = tag.replace(cm.group(0), f' class="{cm.group(1)} {" ".join(classes)}"')
            else:
                tag = re.sub(r'^<(\w+)', lambda t: f'<{t.group(1)} class="{" ".join(classes)}"', tag)
        return tag
    return re.sub(r'<[A-Za-z][^>]*>', fix_tag, svg)

# ---------------------------------------------------------------- research thrust illustrations (original line art)
_ART_HEAD = '<svg viewBox="0 0 360 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">'

ART = {
"grid": _ART_HEAD + """
<g class="card"><rect x="14" y="14" width="332" height="152" rx="12" fill="#fff" stroke="#D5DCE5"/></g>
<!-- towers -->
<g stroke="#044978" stroke-width="1.7">
  <path d="M46 146l12-92h12l12 92M50 122h32M53 100h26M57 78h18M36 122h60M40 100h52M46 78h40"/>
  <path d="M284 146l12-92h12l12 92M288 122h32M291 100h26M295 78h18M274 122h60M278 100h52M284 78h40"/>
</g>
<!-- power lines with moving energy -->
<path d="M46 78Q180 128 284 78M40 100Q180 150 290 100" stroke="#D5DCE5" stroke-width="1.6"/>
<path class="flow" d="M46 78Q180 128 284 78" stroke="#0A777F" stroke-width="2.4"/><path class="flow slow" d="M40 100Q180 150 290 100" stroke="#0A777F" stroke-width="2.4"/>
<!-- substation -->
<rect x="140" y="118" width="80" height="30" rx="5" fill="#044978"/>
<g stroke="#fff" stroke-width="1.2" opacity=".7"><path d="M156 122v22M172 122v22M188 122v22M204 122v22M140 133h80"/></g>
<!-- smart meters -->
<g fill="#fff" stroke="#044978" stroke-width="1.6"><rect x="104" y="30" width="28" height="30" rx="6"/><rect x="166" y="30" width="28" height="30" rx="6"/><rect x="228" y="30" width="28" height="30" rx="6"/></g>
<g stroke="#0A777F" stroke-width="1.7"><path d="M110 48a8 8 0 0 1 16 0M172 48a8 8 0 0 1 16 0M234 48a8 8 0 0 1 16 0M118 48l4-5M180 48l4-6M242 48l3-7"/></g>
<g stroke="#D5DCE5" stroke-width="1.6"><path d="M118 60v58M180 60v58M242 60v58"/></g>
<g stroke="#3BA995" stroke-width="2.2"><path class="flow" d="M118 60v58"/><path class="flow slow" d="M180 60v58"/><path class="flow" d="M242 60v58"/></g>
<!-- shield -->
<path d="M180 70l14 5v10c0 9-6 15-14 18-8-3-14-9-14-18V75z" fill="#3BA995"/><path d="M174 85l4 4 8-9" stroke="#fff" stroke-width="2"/>
<!-- attack bolt deflected -->
<g class="pulse"><path d="M266 64l-14 9 7 2-9 12" stroke="#E25555" stroke-width="2.2"/><circle cx="250" cy="87" r="3" fill="#E25555"/></g>
<path d="M30 148h300" stroke="#D5DCE5" stroke-width="1.2"/>
</svg>""",

"ai": _ART_HEAD + """
<g class="card"><rect x="14" y="14" width="332" height="152" rx="12" fill="#fff" stroke="#D5DCE5"/></g>
<!-- network links with signal -->
<g stroke="#D5DCE5" stroke-width="1.2">
  <path d="M52 62L92 46M52 62L92 78M52 62L92 110M52 92L92 46M52 92L92 78M52 92L92 110M52 92L92 142M52 122L92 78M52 122L92 110M52 122L92 142M100 46L138 78M100 78L138 78M100 110L138 110M100 142L138 110M100 78L138 110M100 110L138 78"/>
</g>
<g stroke="#0A777F" stroke-width="1.6"><path class="flow" d="M52 62L92 46L138 78"/><path class="flow slow" d="M52 122L92 110L138 110"/></g>
<g fill="#044978"><circle cx="52" cy="62" r="7"/><circle cx="52" cy="92" r="7"/><circle cx="52" cy="122" r="7"/><circle cx="92" cy="46" r="7"/><circle cx="92" cy="78" r="7"/><circle cx="92" cy="110" r="7"/><circle cx="92" cy="142" r="7"/></g>
<g fill="#0A777F"><circle cx="138" cy="78" r="7"/><circle cx="138" cy="110" r="7"/></g>
<!-- safety gate -->
<path d="M146 94h26" stroke="#D5DCE5" stroke-width="1.6"/><path class="flow" d="M146 94h26" stroke="#0A777F" stroke-width="2.2"/>
<rect x="174" y="72" width="44" height="44" rx="10" fill="#3BA995"/><path d="M186 94l6 6 12-13" stroke="#fff" stroke-width="2.6"/>
<path d="M220 94h28" stroke="#D5DCE5" stroke-width="1.6"/><path class="flow" d="M220 94h28" stroke="#3BA995" stroke-width="2.2"/><path d="M244 89l6 5-6 5" stroke="#3BA995" stroke-width="2"/>
<!-- turbine -->
<circle cx="292" cy="94" r="34" fill="#F3F7FA" stroke="#D5DCE5"/>
<g class="spin" style="transform-origin:292px 94px"><path d="M292 94l-4-26 8 0zM292 94l22 14-4 7zM292 94l-22 14 4 7z" fill="#044978"/></g>
<circle cx="292" cy="94" r="5" fill="#fff" stroke="#044978" stroke-width="2"/>
<!-- feedback loop -->
<path d="M292 130v22H52v-14" stroke="#3BA995" stroke-width="1.6" stroke-dasharray="4 5" class="flow slow"/><path d="M47 144l5-7 5 7" stroke="#3BA995" stroke-width="1.6"/>
<text x="180" y="150" font-size="11" fill="#5B6B82" text-anchor="middle">learn, check, act</text>
</svg>""",

"fiber": _ART_HEAD + """
<g class="card"><rect x="14" y="14" width="332" height="152" rx="12" fill="#fff" stroke="#D5DCE5"/></g>
<!-- fiber cross-section -->
<circle cx="66" cy="92" r="36" fill="#F3F7FA" stroke="#044978" stroke-width="1.6"/><circle cx="66" cy="92" r="24" stroke="#D5DCE5" stroke-width="1.2"/>
<g fill="#0A777F"><circle cx="66" cy="92" r="4.5"/><circle cx="56" cy="80" r="3.2"/><circle cx="78" cy="82" r="3.2"/><circle cx="54" cy="104" r="3.2"/><circle cx="78" cy="104" r="3.2"/></g>
<g fill="#3BA995" class="pulse"><circle cx="66" cy="92" r="8" opacity=".35"/></g>
<!-- light pulses along the fiber to the spectrum -->
<path d="M104 92h24" stroke="#D5DCE5" stroke-width="1.6"/><path class="flow" d="M104 92h24" stroke="#0A777F" stroke-width="2.6"/>
<!-- spectrum -->
<path d="M132 128h146" stroke="#5B6B82" stroke-width="1.2"/>
<rect x="136" y="70" width="40" height="58" rx="3" fill="#044978" opacity=".85" class="grow" style="transform-origin:156px 128px"/>
<rect x="182" y="52" width="44" height="76" rx="3" fill="#0A777F" class="grow" style="transform-origin:204px 128px;animation-delay:.6s"/>
<rect x="232" y="82" width="44" height="46" rx="3" fill="#3BA995" class="grow" style="transform-origin:254px 128px;animation-delay:1.2s"/>
<g font-size="11" fill="#5B6B82" text-anchor="middle"><text x="156" y="143">S</text><text x="204" y="143">C</text><text x="254" y="143">L</text><text x="205" y="158">multi-band spectrum</text></g>
<!-- 6G mast with expanding waves -->
<path d="M322 148V72M314 148h16" stroke="#044978" stroke-width="1.6"/><path d="M316 72h12l-6-10z" fill="#044978"/>
<g stroke="#0A777F" stroke-width="1.6" fill="none"><path class="pulse" d="M310 64a17 17 0 0 1 24 0"/><path class="pulse" style="animation-delay:.7s" d="M304 56a26 26 0 0 1 36 0"/><path class="pulse" style="animation-delay:1.4s" d="M298 48a34 34 0 0 1 48 0"/></g>
</svg>""",

"edge": _ART_HEAD + """
<g class="card"><rect x="14" y="14" width="332" height="152" rx="12" fill="#fff" stroke="#D5DCE5"/></g>
<!-- links -->
<g stroke="#D5DCE5" stroke-width="1.4"><path d="M96 74h38M168 60l36 12M80 90l18 30M220 90l-18 30M130 134h34M96 74l38-14M148 62v58"/></g>
<g stroke="#0A777F" stroke-width="2"><path class="flow" d="M96 74h38"/><path class="flow slow" d="M168 60l36 12"/><path class="flow" d="M80 90l18 30"/><path class="flow slow" d="M220 90l-18 30"/></g>
<!-- replicas -->
<g fill="#fff" stroke="#044978" stroke-width="1.6"><rect x="62" y="60" width="36" height="28" rx="7"/><rect x="130" y="34" width="36" height="28" rx="7"/><rect x="200" y="60" width="36" height="28" rx="7"/><rect x="96" y="120" width="36" height="28" rx="7"/></g>
<g stroke="#3BA995" stroke-width="2.2"><path d="M72 74l5 5 9-10M140 48l5 5 9-10M210 74l5 5 9-10M106 134l5 5 9-10"/></g>
<!-- faulty replica -->
<g class="pulse"><rect x="164" y="120" width="36" height="28" rx="7" fill="#FDECEC" stroke="#E25555" stroke-width="1.6"/><path d="M176 128l12 12M188 128l-12 12" stroke="#E25555" stroke-width="2.2"/></g>
<!-- drone -->
<g transform="translate(266,56)"><path d="M0 12h44M10 12V6H0M34 12V6h44" stroke="#044978" stroke-width="1.6"/><rect x="13" y="9" width="18" height="10" rx="3" fill="#044978"/><g stroke="#0A777F" stroke-width="1.6" class="spin" style="transform-origin:5px 6px"><path d="M-3 6h16"/></g><g stroke="#0A777F" stroke-width="1.6" class="spin" style="transform-origin:39px 6px"><path d="M31 6h16"/></g></g>
<!-- satellite link -->
<path d="M262 40a40 40 0 0 1 56 0" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow slow" d="M262 40a40 40 0 0 1 56 0" stroke="#3BA995" stroke-width="2"/>
<circle cx="290" cy="24" r="4.5" fill="#3BA995"/>
<path d="M288 74v32" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow" d="M288 74v32" stroke="#0A777F" stroke-width="2"/>
<path d="M288 106l-52 22" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow slow" d="M288 106l-52 22" stroke="#0A777F" stroke-width="2"/>
<text x="288" y="122" font-size="11" fill="#5B6B82" text-anchor="middle">edge</text>
<text x="150" y="162" font-size="11" fill="#5B6B82" text-anchor="middle">consensus with a faulty replica</text>
</svg>""",

"chip": _ART_HEAD + """
<g class="card"><rect x="14" y="14" width="332" height="152" rx="12" fill="#fff" stroke="#D5DCE5"/></g>
<!-- chip -->
<rect x="66" y="48" width="88" height="88" rx="10" fill="#044978"/>
<rect x="88" y="70" width="44" height="44" rx="6" fill="#0A777F"/>
<g stroke="#044978" stroke-width="2"><path d="M82 48V36M100 48V36M118 48V36M136 48V36M82 136v12M100 136v12M118 136v12M136 136v12M66 66H54M66 84H54M66 102H54M66 120H54M154 66h12M154 84h12M154 102h12M154 120h12"/></g>
<rect x="102" y="90" width="16" height="13" rx="2" fill="#fff"/><path d="M105 90v-4a5 5 0 0 1 10 0v4" stroke="#fff" stroke-width="1.8"/>
<!-- data out -->
<path d="M166 92h28" stroke="#D5DCE5" stroke-width="1.6"/><path class="flow" d="M166 92h28" stroke="#0A777F" stroke-width="2.4"/>
<!-- hardware counters -->
<rect x="200" y="94" width="10" height="42" fill="#0A777F" class="grow" style="transform-origin:205px 136px"/>
<rect x="216" y="76" width="10" height="60" fill="#0A777F" class="grow" style="transform-origin:221px 136px;animation-delay:.5s"/>
<rect x="232" y="106" width="10" height="30" fill="#0A777F" class="grow" style="transform-origin:237px 136px;animation-delay:1s"/>
<rect x="248" y="62" width="10" height="74" fill="#0A777F" class="grow" style="transform-origin:253px 136px;animation-delay:1.5s"/>
<g class="pulse"><rect x="264" y="116" width="10" height="20" fill="#E25555"/></g>
<path d="M194 136h90" stroke="#5B6B82" stroke-width="1.2"/>
<text x="239" y="152" font-size="11" fill="#5B6B82" text-anchor="middle">hardware counters</text>
<!-- rack -->
<rect x="296" y="42" width="44" height="98" rx="5" fill="#fff" stroke="#044978" stroke-width="1.6"/>
<g stroke="#D5DCE5" stroke-width="1.1"><path d="M296 62h44M296 82h44M296 102h44M296 122h44"/></g>
<g fill="#3BA995"><circle cx="331" cy="52" r="2.5" class="pulse"/><circle cx="331" cy="72" r="2.5" class="pulse" style="animation-delay:.8s"/><circle cx="331" cy="92" r="2.5" class="pulse" style="animation-delay:1.6s"/><circle cx="331" cy="112" r="2.5" class="pulse" style="animation-delay:.4s"/><circle cx="331" cy="132" r="2.5" class="pulse" style="animation-delay:2s"/></g>
</svg>""",

"health": _ART_HEAD + """
<g class="card"><rect x="14" y="14" width="332" height="152" rx="12" fill="#fff" stroke="#D5DCE5"/></g>
<!-- road with moving lane marks -->
<rect x="24" y="118" width="196" height="26" rx="4" fill="#F3F7FA" stroke="#D5DCE5"/>
<path class="flow slow" d="M30 131h184" stroke="#5B6B82" stroke-width="1.4" stroke-dasharray="10 8"/>
<!-- vehicles -->
<g><path d="M44 118h48l-8-14H52z" fill="#044978"/><path d="M40 118h56v6H40z" fill="#044978" opacity=".85"/><circle cx="52" cy="126" r="4.5" fill="#fff" stroke="#044978" stroke-width="1.6"/><circle cx="84" cy="126" r="4.5" fill="#fff" stroke="#044978" stroke-width="1.6"/></g>
<g><path d="M130 118h48l-8-14h-32z" fill="#0A777F"/><path d="M126 118h56v6h-56z" fill="#0A777F" opacity=".85"/><circle cx="138" cy="126" r="4.5" fill="#fff" stroke="#0A777F" stroke-width="1.6"/><circle cx="170" cy="126" r="4.5" fill="#fff" stroke="#0A777F" stroke-width="1.6"/></g>
<path d="M92 96q32-30 64 0" stroke="#3BA995" stroke-width="1.8" stroke-dasharray="3 5" class="flow"/>
<g stroke="#3BA995" stroke-width="1.6" class="pulse"><path d="M68 98v-9M62 93l6-6 6 6M154 98v-9M148 93l6-6 6 6"/></g>
<!-- bridge with sensors -->
<path d="M232 144h104M244 144V100M324 144V100M232 100h104" stroke="#044978" stroke-width="1.6"/>
<path d="M244 100q40-38 80 0" stroke="#044978" stroke-width="1.6"/><path d="M264 144V88M284 144V80M304 144V88" stroke="#D5DCE5" stroke-width="1.2"/>
<g fill="#3BA995"><circle cx="264" cy="88" r="3.5" class="pulse"/><circle cx="284" cy="80" r="3.5" class="pulse" style="animation-delay:.7s"/><circle cx="304" cy="88" r="3.5" class="pulse" style="animation-delay:1.4s"/></g>
<!-- hospital and ECG -->
<rect x="236" y="28" width="40" height="36" rx="6" fill="#0A777F"/><path d="M256 36v20M246 46h20" stroke="#fff" stroke-width="3"/>
<path class="trace" pathLength="100" d="M284 48h10l6-14 8 28 8-20 6 6h14" stroke="#3BA995" stroke-width="2"/>
<!-- data uplink from vehicles to the hospital and bridge -->
<path d="M120 58h108" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow" d="M120 58h108" stroke="#0A777F" stroke-width="2"/>
<circle cx="120" cy="58" r="4.5" fill="#0A777F"/><path d="M120 62v34" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow slow" d="M120 62v34" stroke="#0A777F" stroke-width="2"/>
<text x="180" y="162" font-size="11" fill="#5B6B82" text-anchor="middle">connected roads, hospitals, and structures</text>
</svg>""",
}
HUB = """<svg viewBox="0 0 1200 690" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="hubTitle hubDesc" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">
<title id="hubTitle">SCyPS serves as the center hub</title><desc id="hubDesc">Five activities radiate from the center: research on secure and resilient cyber-physical systems, shared testbeds and instruments, training the workforce, partnership with industry and agencies, and open-source tools and technology transfer.</desc>
<defs><marker id="hubar" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker></defs>
<path d="M600 211L600 161" stroke="#0A777F" stroke-width="2.6" marker-end="url(#hubar)"/>
<path d="M721 306L752 299" stroke="#0A777F" stroke-width="2.6" marker-end="url(#hubar)"/>
<path d="M688 423L731 466" stroke="#0A777F" stroke-width="2.6" marker-end="url(#hubar)"/>
<path d="M512 423L469 466" stroke="#0A777F" stroke-width="2.6" marker-end="url(#hubar)"/>
<path d="M479 306L448 299" stroke="#0A777F" stroke-width="2.6" marker-end="url(#hubar)"/>
<circle cx="600" cy="335" r="112" fill="#044978"/>
<circle cx="600" cy="335" r="112" fill="none" stroke="#0A777F" stroke-width="3" class="flow slow"/>
<text x="600" y="327" text-anchor="middle" font-size="31" font-weight="600" fill="#FFFFFF">SCyPS</text>
<text x="600" y="357" text-anchor="middle" font-size="16" fill="#C9DCEA">serves as the</text>
<text x="600" y="379" text-anchor="middle" font-size="16" fill="#C9DCEA">center hub</text>
<g class="card"><rect x="448" y="37" width="304" height="112" rx="14" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"/></g>
<circle cx="600" cy="63" r="14" fill="#3BA995"/>
<text x="600" y="68" text-anchor="middle" font-size="14" font-weight="700" fill="#062B24">1</text>
<text x="600" y="103" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">Research on secure, resilient</text>
<text x="600" y="125" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">cyber-physical systems</text>
<g class="card"><rect x="764" y="204" width="304" height="112" rx="14" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"/></g>
<circle cx="916" cy="230" r="14" fill="#3BA995"/>
<text x="916" y="235" text-anchor="middle" font-size="14" font-weight="700" fill="#062B24">2</text>
<text x="916" y="270" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">Shared testbeds and instruments,</text>
<text x="916" y="292" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">including SUMMIT</text>
<g class="card"><rect x="643" y="475" width="304" height="112" rx="14" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"/></g>
<circle cx="795" cy="501" r="14" fill="#3BA995"/>
<text x="795" y="506" text-anchor="middle" font-size="14" font-weight="700" fill="#062B24">3</text>
<text x="795" y="541" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">Training the cyber-physical</text>
<text x="795" y="563" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">systems workforce</text>
<g class="card"><rect x="253" y="475" width="304" height="112" rx="14" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"/></g>
<circle cx="405" cy="501" r="14" fill="#3BA995"/>
<text x="405" y="506" text-anchor="middle" font-size="14" font-weight="700" fill="#062B24">4</text>
<text x="405" y="541" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">Industry, agency, and</text>
<text x="405" y="563" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">community partnership</text>
<g class="card"><rect x="132" y="204" width="304" height="112" rx="14" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"/></g>
<circle cx="284" cy="230" r="14" fill="#3BA995"/>
<text x="284" y="235" text-anchor="middle" font-size="14" font-weight="700" fill="#062B24">5</text>
<text x="284" y="270" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">Open-source tools and</text>
<text x="284" y="292" text-anchor="middle" font-size="15.5" font-weight="600" fill="#0E2036">technology transfer</text>
<text x="600" y="674" text-anchor="middle" font-size="16" fill="#5B6B82">across energy and power, transportation, and healthcare</text>
</svg>"""
HUB = theme_svg(HUB)

ART["hpc"] = """<svg viewBox="0 0 360 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">
<rect x="28" y="30" width="86" height="120" rx="8" fill="#FFFFFF" stroke="#044978" stroke-width="2.4"/>
<g stroke="#D5DCE5" stroke-width="1.4"><path d="M28 60h86M28 90h86M28 120h86"/></g>
<g stroke="#0A777F" stroke-width="2"><path d="M40 45h34M40 75h26M40 105h38M40 135h22"/></g>
<g fill="#3BA995"><circle cx="104" cy="45" r="3" class="pulse"/><circle cx="104" cy="75" r="3" class="pulse" style="animation-delay:.6s"/><circle cx="104" cy="105" r="3" class="pulse" style="animation-delay:1.2s"/><circle cx="104" cy="135" r="3" class="pulse" style="animation-delay:1.8s"/></g>
<path d="M120 90h26" stroke="#0A777F" stroke-width="2.4" class="flow"/>
<path d="M158 140h180" stroke="#D5DCE5" stroke-width="1.6"/>
<rect x="166" y="86" width="18" height="54" class="grow" style="transform-origin:175px 140px" fill="#0A777F"/>
<rect x="192" y="66" width="18" height="74" class="grow" style="transform-origin:201px 140px;animation-delay:.3s" fill="#0A777F"/>
<rect x="218" y="100" width="18" height="40" class="grow" style="transform-origin:227px 140px;animation-delay:.6s" fill="#0A777F"/>
<rect x="244" y="56" width="18" height="84" class="grow" style="transform-origin:253px 140px;animation-delay:.9s" fill="#0A777F"/>
<g class="pulse"><rect x="270" y="112" width="18" height="28" fill="#E25555"/><circle cx="279" cy="100" r="6" fill="#E25555"/></g>
<rect x="296" y="90" width="18" height="50" fill="#0A777F"/>
<text x="248" y="166" text-anchor="middle" font-size="11" fill="#5B6B82">an outlier with no error raised</text>
</svg>"""
ART["nuclear"] = """<svg viewBox="0 0 360 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M40 150V92a44 44 0 0 1 88 0v58z" fill="#FFFFFF" stroke="#044978" stroke-width="3"/>
<path d="M40 108h88" stroke="#D5DCE5" stroke-width="1.6"/>
<circle cx="84" cy="124" r="18" stroke="#0A777F" stroke-width="3"/><circle cx="84" cy="124" r="5" fill="#0A777F"/>
<g stroke="#3BA995" stroke-width="2.6"><path d="M84 106a18 18 0 0 1 16 27M84 142a18 18 0 0 1-16-27"/></g>
<path d="M146 124h34" stroke="#3BA995" stroke-width="2.6" stroke-dasharray="3 8" class="flow"/>
<rect x="188" y="96" width="34" height="56" rx="6" fill="#044978"/><rect x="195" y="103" width="20" height="26" rx="3" fill="#0A777F"/>
<circle cx="205" cy="140" r="3.5" fill="#3BA995" class="pulse"/>
<path d="M244 148h96M244 148V70" stroke="#D5DCE5" stroke-width="1.6"/>
<path class="trace" pathLength="100" d="M246 142c10-2 14-14 20-14s4 12 10 13 8-58 15-58 6 50 13 50 5-20 12-20 8 15 14 15 4-5 12-7" stroke="#0A777F" stroke-width="2.4"/>
<path d="M120 62l20 7v17c0 14-8 23-20 28-12-5-20-14-20-28V69z" fill="#3BA995"/>
<path d="M110 85l6 6 13-14" stroke="#FFFFFF" stroke-width="4"/>
<text x="180" y="174" text-anchor="middle" font-size="11" fill="#5B6B82">measure, verify, and secure</text>
</svg>"""
ORG = """<svg viewBox="0 0 1200 660" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="orgTitle orgDesc" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">
<title id="orgTitle">How the center is organized</title>
<desc id="orgDesc">A director and an executive committee, advised by an external advisory board and an industry partners council; eight research thrusts each with a named lead; and the laboratories and instruments the work runs on.</desc>
<rect width="1200" height="660" fill="#FFFFFF"/>

<!-- director -->
<g class="card"><rect x="440" y="24" width="320" height="92" rx="14" fill="#044978"/></g>
<text x="600" y="58" text-anchor="middle" font-size="20" font-weight="600" fill="#FFFFFF">Director</text>
<text x="600" y="84" text-anchor="middle" font-size="15" fill="#C9DCEA">Vinod M. Vokkarane</text>
<text x="600" y="104" text-anchor="middle" font-size="13" fill="#9FC4DF">Electrical and Computer Engineering</text>

<!-- advisory bodies -->
<g class="card" fill="#FFFFFF" stroke="#0A777F" stroke-width="1.8"><rect x="40" y="34" width="330" height="72" rx="12"/><rect x="830" y="34" width="330" height="72" rx="12"/></g>
<text x="205" y="62" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">External Advisory Board</text>
<text x="205" y="84" text-anchor="middle" font-size="13" fill="#5B6B82">agency, industry, and academic advisors</text>
<text x="995" y="62" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">Industry Partners Council</text>
<text x="995" y="84" text-anchor="middle" font-size="13" fill="#5B6B82">companies working with the center</text>
<g stroke="#0A777F" stroke-width="2.4"><path d="M370 70h70M760 70h70"/></g>

<!-- executive committee -->
<g class="card"><rect x="390" y="156" width="420" height="76" rx="14" fill="#0A777F"/></g>
<text x="600" y="186" text-anchor="middle" font-size="18" font-weight="600" fill="#FFFFFF">Executive Committee</text>
<text x="600" y="211" text-anchor="middle" font-size="13" fill="#CFE8E7">membership, priorities, instrument access, seed funding</text>
<path d="M600 116v40" stroke="#044978" stroke-width="2.6"/>

<!-- thrust band -->
<rect x="28" y="266" width="1144" height="196" rx="16" fill="#F3F7FA"/>
<g class="card"><rect x="440" y="252" width="320" height="34" rx="17" fill="#CDDFF0"/></g>
<text x="600" y="274" text-anchor="middle" font-size="14" font-weight="600" fill="#044978">Eight research thrusts, each with a lead</text>
<path d="M600 232v20" stroke="#0A777F" stroke-width="2.4"/>
"""

_TB = [(["Smart grid", "security"], "Vokkarane"), (["AI for", "cyber-physical", "control"], "Luo"),
       (["Optical and", "6G transport"], "Vokkarane"), (["Fault-tolerant", "edge computing"], "Tseng"),
       (["Hardware", "security"], "Arias"), (["HPC and", "data integrity"], "Son"),
       (["Connected", "transportation"], "Xie"), (["Nuclear energy", "and security"], "Aghara")]
_bw, _gap, _x0, _y0 = 130, 12, 46, 306
_boxes = []
for _i, (_lines, _who) in enumerate(_TB):
    _x = _x0 + _i * (_bw + _gap)
    # title block vertically centred in the space above the rule, whatever its line count
    _top = _y0 + (34 if len(_lines) == 2 else 26)
    _t = "".join(f'<text x="{_x + _bw/2}" y="{_top + k*16}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#0E2036">{ln}</text>'
                 for k, ln in enumerate(_lines))
    _boxes.append(
        f'<g class="card"><rect x="{_x}" y="{_y0}" width="{_bw}" height="110" rx="11" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"/></g>'
        f'<rect x="{_x}" y="{_y0}" width="{_bw}" height="5" rx="2.5" fill="#0A777F"/>'
        + _t +
        f'<path d="M{_x + 20} {_y0 + 72}h{_bw - 40}" stroke="#D5DCE5" stroke-width="1"/>'
        f'<text x="{_x + _bw/2}" y="{_y0 + 94}" text-anchor="middle" font-size="12.5" fill="#5B6B82">{_who} leads</text>'
        f'<path d="M{_x + _bw/2} 286v20" stroke="#D5DCE5" stroke-width="1"/>')
ORG = ORG.replace("</svg>", "") + "".join(_boxes) + """
<g class="card" fill="#FFFFFF" stroke="#3BA995" stroke-width="1.8"><rect x="46" y="494" width="550" height="128" rx="14"/><rect x="616" y="494" width="538" height="128" rx="14"/></g>
<text x="321" y="526" text-anchor="middle" font-size="16" font-weight="600" fill="#0E2036">People</text>
<text x="321" y="554" text-anchor="middle" font-size="13.5" fill="#5B6B82">Faculty from four UMass Lowell colleges, external collaborators at</text>
<text x="321" y="576" text-anchor="middle" font-size="13.5" fill="#5B6B82">NYU, West Virginia, Louisiana, Red Hat, and Navia Energy,</text>
<text x="321" y="598" text-anchor="middle" font-size="13.5" fill="#5B6B82">doctoral students, and postdoctoral researchers</text>
<text x="885" y="526" text-anchor="middle" font-size="16" font-weight="600" fill="#0E2036">Instruments</text>
<text x="885" y="554" text-anchor="middle" font-size="13.5" fill="#5B6B82">The SUMMIT federated testbed, the NATIG co-simulation testbed,</text>
<text x="885" y="576" text-anchor="middle" font-size="13.5" fill="#5B6B82">the open-source FUSION framework, and the member laboratories:</text>
<text x="885" y="598" text-anchor="middle" font-size="13.5" fill="#5B6B82">ACNL, INSSL, PERC and RURI, LoCSST, CDH, and CEI</text>
<path d="M321 462v32M885 462v32" stroke="#D5DCE5" stroke-width="1.4"/>
</svg>"""
ORG = theme_svg(ORG)

ART = {k: theme_svg(v) for k, v in ART.items()}
TOOL_ART = {
"fusion": """<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">
<rect width="640" height="300" fill="#FFFFFF"/>
<!-- optical mesh -->
<g stroke="#D5DCE5" stroke-width="2.5"><path d="M70 150L170 80M170 80L290 150M290 150L400 80M70 150L170 220M170 220L290 150M290 150L400 220M170 80L170 220M400 80L400 220M70 150L290 150"/></g>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M70 150L170 80L290 150L400 80"/><path class="flow slow" d="M70 150L170 220L290 150L400 220"/></g>
<g fill="#044978"><circle cx="70" cy="150" r="9"/><circle cx="170" cy="80" r="9"/><circle cx="170" cy="220" r="9"/><circle cx="290" cy="150" r="9"/><circle cx="400" cy="80" r="9"/><circle cx="400" cy="220" r="9"/></g>
<g fill="#FFFFFF"><circle cx="70" cy="150" r="3"/><circle cx="170" cy="80" r="3"/><circle cx="170" cy="220" r="3"/><circle cx="290" cy="150" r="3"/><circle cx="400" cy="80" r="3"/><circle cx="400" cy="220" r="3"/></g>
<text x="235" y="272" text-anchor="middle" font-size="12.5" fill="#5B6B82">multi-band, multi-core lightpath requests</text>
<!-- benchmark panel -->
<g class="card"><rect x="452" y="38" width="158" height="200" rx="10" fill="#F3F7FA" stroke="#D5DCE5"/></g>
<text x="531" y="62" text-anchor="middle" font-size="12.5" font-weight="600" fill="#0E2036">reproducible run</text>
<g stroke="#D5DCE5" stroke-width="1.4"><path d="M470 210h124M470 210V78"/></g>
<rect x="480" y="150" width="20" height="60" class="grow" style="transform-origin:490px 210px" fill="#044978"/>
<rect x="508" y="120" width="20" height="90" class="grow" style="transform-origin:518px 210px;animation-delay:.4s" fill="#0A777F"/>
<rect x="536" y="170" width="20" height="40" class="grow" style="transform-origin:546px 210px;animation-delay:.8s" fill="#3BA995"/>
<rect x="564" y="100" width="20" height="110" class="grow" style="transform-origin:574px 210px;animation-delay:1.2s" fill="#044978"/>
<text x="531" y="230" text-anchor="middle" font-size="11.5" fill="#5B6B82">blocking, capacity, QoT</text>
<path d="M410 150h36" stroke="#0A777F" stroke-width="3" class="flow"/>
<text x="235" y="40" text-anchor="middle" font-size="12.5" fill="#5B6B82">same topology, same seed, same result</text>
</svg>""",
"cosim": """<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="640" height="300" fill="#FFFFFF"/>
<!-- the three containers -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5">
  <rect x="40" y="38" width="160" height="84" rx="10"/><rect x="240" y="38" width="160" height="84" rx="10"/><rect x="440" y="38" width="160" height="84" rx="10"/>
</g>
<g fill="#044978"><rect x="40" y="38" width="160" height="26" rx="10"/><rect x="40" y="54" width="160" height="10"/>
  <rect x="240" y="38" width="160" height="26" rx="10"/><rect x="240" y="54" width="160" height="10"/>
  <rect x="440" y="38" width="160" height="26" rx="10"/><rect x="440" y="54" width="160" height="10"/></g>
<g font-size="14" font-weight="600" fill="#FFFFFF" text-anchor="middle">
  <text x="120" y="57">GridLAB-D</text><text x="320" y="57">HELICS</text><text x="520" y="57">ns-3</text></g>
<g font-size="12.5" fill="#5B6B82" text-anchor="middle">
  <text x="120" y="88">distribution feeder</text><text x="120" y="106">IEEE 123-bus</text>
  <text x="320" y="88">federation broker</text><text x="320" y="106">time synchronization</text>
  <text x="520" y="88">communication</text><text x="520" y="106">network model</text></g>
<!-- broker links -->
<g stroke="#D5DCE5" stroke-width="2.5"><path d="M200 80h40M400 80h40"/></g>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M200 80h40"/><path class="flow slow" d="M440 80H400"/></g>
<!-- docker frame around the three -->
<rect x="24" y="24" width="592" height="112" rx="14" stroke="#0A777F" stroke-width="1.6" stroke-dasharray="6 7"/>
<text x="34" y="18" font-size="12.5" fill="#0A777F">one Docker image, one command to run</text>
<!-- control centre and device, DNP3 between them -->
<g class="card"><rect x="40" y="196" width="150" height="66" rx="10" fill="#044978"/></g>
<text x="115" y="226" text-anchor="middle" font-size="14" font-weight="600" fill="#FFFFFF">control center</text>
<text x="115" y="246" text-anchor="middle" font-size="12" fill="#C9DCEA">SCADA master</text>
<g class="card"><rect x="450" y="196" width="150" height="66" rx="10" fill="#FFFFFF" stroke="#044978" stroke-width="2"/></g>
<text x="525" y="226" text-anchor="middle" font-size="14" font-weight="600" fill="#0E2036">field devices</text>
<text x="525" y="246" text-anchor="middle" font-size="12" fill="#5B6B82">relays and meters</text>
<path d="M190 229h260" stroke="#D5DCE5" stroke-width="2.5"/>
<path class="flow" d="M190 229h260" stroke="#3BA995" stroke-width="3"/>
<text x="320" y="219" text-anchor="middle" font-size="12.5" fill="#5B6B82">DNP3 traffic</text>
<g class="pulse"><path d="M356 196l-22 16 12 3-14 18" stroke="#E25555" stroke-width="2.6"/></g>
<text x="320" y="276" text-anchor="middle" font-size="12.5" fill="#5B6B82">attack and fault scenarios injected on the wire</text>
<g stroke="#D5DCE5" stroke-width="2" stroke-dasharray="4 6"><path d="M115 196v-60M525 196v-60"/></g>
</svg>""",
"summit_tool": """<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="640" height="300" fill="#FFFFFF"/>
<!-- wide-area cloud -->
<path d="M232 76c-16-34 46-54 64-30 16-24 66-14 66 16 28-3 40 34 14 45H246c-27-2-31-31-14-31z" fill="#F3F7FA" stroke="#D5DCE5" stroke-width="1.6"/>
<text x="320" y="84" text-anchor="middle" font-size="12.5" fill="#5B6B82">wide-area SDN over the Internet</text>
<!-- three sites -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5">
  <rect x="34" y="150" width="170" height="112" rx="10"/><rect x="235" y="150" width="170" height="112" rx="10"/><rect x="436" y="150" width="170" height="112" rx="10"/>
</g>
<g font-size="14" font-weight="600" fill="#0E2036" text-anchor="middle">
  <text x="119" y="174">UMass Lowell</text><text x="320" y="174">NYU Tandon</text><text x="521" y="174">West Virginia</text></g>
<g font-size="11.5" fill="#5B6B82" text-anchor="middle">
  <text x="119" y="191">lead site</text><text x="320" y="191">federation site</text><text x="521" y="191">federation site</text></g>
<!-- RTDS racks -->
<g fill="#044978"><rect x="92" y="200" width="54" height="48" rx="5"/><rect x="293" y="200" width="54" height="48" rx="5"/><rect x="494" y="200" width="54" height="48" rx="5"/></g>
<g stroke="#3BA995" stroke-width="2"><path d="M100 212h38M100 224h38M100 236h38M301 212h38M301 224h38M301 236h38M502 212h38M502 224h38M502 236h38"/></g>
<g fill="#3BA995"><circle cx="140" cy="206" r="2.6" class="pulse"/><circle cx="341" cy="206" r="2.6" class="pulse" style="animation-delay:.7s"/><circle cx="542" cy="206" r="2.6" class="pulse" style="animation-delay:1.4s"/></g>
<text x="320" y="284" text-anchor="middle" font-size="12.5" fill="#5B6B82">real-time simulation with hardware in the loop at every site</text>
<!-- links up to the cloud -->
<g stroke="#D5DCE5" stroke-width="2.5"><path d="M119 150v-38M320 150v-46M521 150v-38"/></g>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M119 150v-38"/><path class="flow slow" d="M320 150v-46"/><path class="flow" d="M521 150v-38"/></g>
<!-- hardware in the loop badge -->
<g class="card"><rect x="34" y="24" width="150" height="46" rx="9" fill="#FFFFFF" stroke="#0A777F" stroke-width="1.6"/></g>
<text x="109" y="43" text-anchor="middle" font-size="12" font-weight="600" fill="#0A777F">relays, controllers</text>
<text x="109" y="59" text-anchor="middle" font-size="11" fill="#5B6B82">hardware in the loop</text>
<path d="M109 70v72" stroke="#3BA995" stroke-width="2.2" stroke-dasharray="5 7" class="flow slow"/>
</svg>""",
}
TOOL_ART = {k: theme_svg(v) for k, v in TOOL_ART.items()}

LAB_ART = {
"acnl": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<g class="card"><rect x="250" y="40" width="220" height="60" rx="12" fill="#044978"/></g>
<text x="360" y="77" text-anchor="middle" font-size="17" font-weight="600" fill="#FFFFFF">SDN controller</text>
<g stroke="#D5DCE5" stroke-width="2" stroke-dasharray="4 7"><path d="M300 100L262 160M360 100L398 238M420 100L536 160"/></g>
<!-- mesh -->
<g stroke="#D5DCE5" stroke-width="3"><path d="M120 250L260 170M260 170L400 250M400 250L540 170M120 250L260 330M260 330L400 250M400 250L540 330M260 170L260 330M540 170L540 330M120 250L400 250"/></g>
<g stroke="#0A777F" stroke-width="3.4"><path class="flow" d="M120 250L260 170L400 250L540 170"/><path class="flow slow" d="M120 250L260 330L400 250L540 330"/></g>
<g fill="#044978"><circle cx="120" cy="250" r="12"/><circle cx="260" cy="170" r="12"/><circle cx="260" cy="330" r="12"/><circle cx="400" cy="250" r="12"/><circle cx="540" cy="170" r="12"/><circle cx="540" cy="330" r="12"/></g>
<g fill="#FFFFFF"><circle cx="120" cy="250" r="4"/><circle cx="260" cy="170" r="4"/><circle cx="260" cy="330" r="4"/><circle cx="400" cy="250" r="4"/><circle cx="540" cy="170" r="4"/><circle cx="540" cy="330" r="4"/></g>
<text x="360" y="378" text-anchor="middle" font-size="14" fill="#5B6B82">elastic optical mesh, multi-band and multi-core</text>
<!-- spectrum readout -->
<g class="card"><rect x="40" y="400" width="640" height="44" rx="10" fill="#F3F7FA" stroke="#D5DCE5"/></g>
<rect x="60" y="410" width="90" height="24" rx="3" fill="#044978" class="grow" style="transform-origin:105px 434px;"/>
<rect x="160" y="410" width="60" height="24" rx="3" fill="#0A777F" class="grow" style="transform-origin:190px 434px;animation-delay:.5s"/>
<rect x="230" y="410" width="120" height="24" rx="3" fill="#3BA995" class="grow" style="transform-origin:290px 434px;animation-delay:1s"/>
<rect x="360" y="410" width="80" height="24" rx="3" fill="#044978" class="grow" style="transform-origin:400px 434px;animation-delay:1.5s"/>
<rect x="450" y="410" width="140" height="24" rx="3" fill="#0A777F" class="grow" style="transform-origin:520px 434px;animation-delay:2s"/>
<rect x="600" y="410" width="60" height="24" rx="3" fill="#D5DCE5"/>
<text x="670" y="468" text-anchor="end" font-size="12" fill="#5B6B82">spectrum allocation, S / C / L bands</text>
</svg>""",
"summit": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<!-- wide area cloud -->
<path d="M240 118c-20-44 60-70 84-38 20-30 84-18 84 20 36-4 52 44 18 58H256c-34-2-40-40-16-40z" fill="#F3F7FA" stroke="#D5DCE5" stroke-width="2"/>
<text x="360" y="128" text-anchor="middle" font-size="13" fill="#5B6B82">wide-area SDN over the Internet</text>
<!-- sites -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="1.5"><rect x="40" y="290" width="200" height="150" rx="14"/><rect x="260" y="290" width="200" height="150" rx="14"/><rect x="480" y="290" width="200" height="150" rx="14"/></g>
<g font-size="15" font-weight="600" fill="#0E2036" text-anchor="middle"><text x="140" y="322">UMass Lowell</text><text x="360" y="322">NYU Tandon</text><text x="580" y="322">West Virginia</text></g>
<g font-size="12" fill="#5B6B82" text-anchor="middle"><text x="140" y="340">lead site, RTDS</text><text x="360" y="340">federation site</text><text x="580" y="340">federation site</text></g>
<!-- simulator racks -->
<g fill="#044978"><rect x="110" y="352" width="60" height="76" rx="6"/><rect x="330" y="360" width="60" height="68" rx="6"/><rect x="550" y="360" width="60" height="68" rx="6"/></g>
<g stroke="#3BA995" stroke-width="2.4"><path d="M120 366h40M120 380h40M120 394h40M120 408h40M340 374h40M340 388h40M340 402h40M560 374h40M560 388h40M560 402h40"/></g>
<g fill="#3BA995"><circle cx="164" cy="416" r="3" class="pulse"/><circle cx="384" cy="416" r="3" class="pulse" style="animation-delay:.7s"/><circle cx="604" cy="416" r="3" class="pulse" style="animation-delay:1.4s"/></g>
<!-- links to the cloud -->
<g stroke="#D5DCE5" stroke-width="3"><path d="M140 290V170M360 290V160M580 290V170"/></g>
<g stroke="#0A777F" stroke-width="3.4"><path class="flow" d="M140 290V170"/><path class="flow slow" d="M360 290V160"/><path class="flow" d="M580 290V170"/></g>
<g stroke="#D5DCE5" stroke-width="2"><path d="M140 170Q250 100 360 160M360 160Q470 100 580 170"/></g>
<!-- hardware in the loop -->
<g class="card"><rect x="40" y="40" width="150" height="56" rx="10" fill="#FFFFFF" stroke="#0A777F" stroke-width="2"/></g>
<text x="115" y="63" text-anchor="middle" font-size="12.5" font-weight="600" fill="#0A777F">relays and controllers</text>
<text x="115" y="82" text-anchor="middle" font-size="11.5" fill="#5B6B82">hardware in the loop</text>
<path d="M115 96v170" stroke="#3BA995" stroke-width="2.4" stroke-dasharray="6 8" class="flow slow"/>
<text x="360" y="466" text-anchor="middle" font-size="13" fill="#5B6B82">one instrument across three universities</text>
</svg>""",
"inssl": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<!-- containment building -->
<path d="M70 420V270a110 110 0 0 1 220 0v150z" fill="#F3F7FA" stroke="#044978" stroke-width="3"/>
<path d="M70 300h220" stroke="#D5DCE5" stroke-width="2"/>
<circle cx="180" cy="330" r="38" stroke="#0A777F" stroke-width="3"/>
<circle cx="180" cy="330" r="11" fill="#0A777F"/>
<g stroke="#3BA995" stroke-width="3"><path d="M180 292a38 38 0 0 1 33 57M180 368a38 38 0 0 1-33-57"/></g>
<text x="180" y="452" text-anchor="middle" font-size="13" fill="#5B6B82">research reactor and safeguards</text>
<!-- detector -->
<g class="card"><rect x="340" y="250" width="70" height="120" rx="10" fill="#044978"/></g>
<rect x="352" y="262" width="46" height="60" rx="6" fill="#0A777F"/>
<g fill="#3BA995"><circle cx="375" cy="345" r="5" class="pulse"/></g>
<text x="375" y="392" text-anchor="middle" font-size="12" fill="#5B6B82">detector</text>
<!-- counts travelling from source to detector -->
<g stroke="#3BA995" stroke-width="2.6" stroke-dasharray="3 9"><path class="flow" d="M222 330H338"/></g>
<!-- spectrum -->
<g class="card"><rect x="440" y="60" width="240" height="300" rx="14" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<text x="560" y="86" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">gamma spectrum</text>
<path d="M460 330h200M460 330V100" stroke="#5B6B82" stroke-width="1.6"/>
<path class="trace" pathLength="100" d="M462 318c20-4 30-30 40-30s8 24 20 26 14-120 30-120 12 100 26 100 10-40 24-40 16 30 28 30 8-10 24-14" stroke="#0A777F" stroke-width="2.6"/>
<path d="M462 318c20-4 30-30 40-30s8 24 20 26 14-120 30-120 12 100 26 100 10-40 24-40 16 30 28 30 8-10 24-14" stroke="#D5DCE5" stroke-width="2"/>
<g fill="#3BA995"><circle cx="552" cy="194" r="4" class="pulse"/><circle cx="602" cy="264" r="4" class="pulse" style="animation-delay:.8s"/></g>
<text x="560" y="350" text-anchor="middle" font-size="11.5" fill="#5B6B82">energy</text>
<!-- shield badge -->
<path d="M560 400l30 10v26c0 22-13 36-30 44-17-8-30-22-30-44v-26z" fill="#3BA995"/>
<path d="M546 434l9 9 20-22" stroke="#FFFFFF" stroke-width="5"/>
</svg>""",
"perc": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<!-- substrate -->
<path d="M80 380 L400 380 L520 300 L200 300 Z" fill="#F3F7FA" stroke="#D5DCE5" stroke-width="2"/>
<!-- printed traces, drawn in over time -->
<g stroke="#044978" stroke-width="4"><path d="M150 352h80l30-20h60l30 20h70l40-30"/></g>
<g stroke="#0A777F" stroke-width="3.4"><path d="M170 330h60l30-20h80"/></g>
<path class="flow" d="M150 352h80l30-20h60l30 20h70l40-30" stroke="#3BA995" stroke-width="2" stroke-dasharray="4 10"/>
<!-- antenna spiral -->
<path d="M420 320a26 26 0 1 1 -20 30a18 18 0 1 0 14 -22a10 10 0 1 1 -8 12" stroke="#044978" stroke-width="3"/>
<!-- print head -->
<g class="card"><rect x="300" y="60" width="90" height="130" rx="10" fill="#044978"/></g>
<rect x="318" y="76" width="54" height="30" rx="4" fill="#0A777F"/>
<path d="M345 190v40" stroke="#044978" stroke-width="8"/>
<path d="M345 232l-10 40h20z" fill="#0A777F"/>
<g fill="#3BA995"><circle cx="345" cy="285" r="3" class="pulse"/><circle cx="341" cy="298" r="2.5" class="pulse" style="animation-delay:.4s"/><circle cx="349" cy="310" r="2.5" class="pulse" style="animation-delay:.8s"/></g>
<text x="345" y="50" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">aerosol-jet head</text>
<!-- gantry -->
<path d="M120 200H620" stroke="#D5DCE5" stroke-width="6"/>
<!-- RF output -->
<g stroke="#3BA995" stroke-width="2.6"><path class="pulse" d="M560 250a30 30 0 0 1 0 60"/><path class="pulse" style="animation-delay:.6s" d="M578 236a48 48 0 0 1 0 88"/><path class="pulse" style="animation-delay:1.2s" d="M596 222a66 66 0 0 1 0 116"/></g>
<text x="470" y="440" text-anchor="middle" font-size="13" fill="#5B6B82">printed RF antenna on a flexible substrate</text>
<g class="card"><rect x="40" y="40" width="170" height="52" rx="10" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<text x="125" y="62" text-anchor="middle" font-size="12" font-weight="600" fill="#0E2036">functional inks</text>
<text x="125" y="80" text-anchor="middle" font-size="11" fill="#5B6B82">conductive, dielectric, sensing</text>
</svg>""",
"locsst": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<rect width="720" height="480" fill="#F3F7FA"/>
<!-- stars -->
<g fill="#044978"><circle cx="90" cy="60" r="2" class="pulse"/><circle cx="200" cy="40" r="1.6" class="pulse" style="animation-delay:.5s"/><circle cx="330" cy="70" r="2.2" class="pulse" style="animation-delay:1s"/><circle cx="470" cy="34" r="1.6" class="pulse" style="animation-delay:1.5s"/><circle cx="620" cy="66" r="2" class="pulse" style="animation-delay:2s"/><circle cx="560" cy="120" r="1.4"/><circle cx="140" cy="130" r="1.4"/></g>
<!-- balloon -->
<ellipse cx="180" cy="150" rx="70" ry="88" fill="#FFFFFF" stroke="#044978" stroke-width="3"/>
<path d="M150 236l30 40 30-40" stroke="#044978" stroke-width="2.4"/>
<!-- payload with telescope -->
<g class="card"><rect x="150" y="276" width="60" height="50" rx="8" fill="#044978"/></g>
<path d="M210 292l60-24" stroke="#0A777F" stroke-width="8"/>
<circle cx="272" cy="266" r="7" fill="#3BA995"/>
<text x="180" y="356" text-anchor="middle" font-size="12" fill="#5B6B82">balloon payload</text>
<!-- light path into the spectrograph -->
<path d="M282 262L470 150" stroke="#3BA995" stroke-width="2.4" stroke-dasharray="4 8" class="flow slow"/>
<!-- spectrograph output: bands -->
<g class="card"><rect x="400" y="200" width="280" height="200" rx="14" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<text x="540" y="228" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">hyperspectral imager</text>
<g><rect x="420" y="244" width="240" height="18" fill="#044978" opacity=".9"/><rect x="420" y="266" width="240" height="18" fill="#0A777F" opacity=".9"/><rect x="420" y="288" width="240" height="18" fill="#3BA995" opacity=".9"/><rect x="420" y="310" width="240" height="18" fill="#3BA995" opacity=".5"/></g>
<g font-size="11" fill="#FFFFFF" font-weight="600"><text x="428" y="257">UV</text><text x="428" y="279">visible</text><text x="428" y="301">near IR</text></g>
<path class="trace" pathLength="100" d="M420 372c30-6 40-40 60-40s20 30 40 30 16-22 36-22 18 26 40 26 22-12 44-10" stroke="#044978" stroke-width="2.4"/>
<path d="M420 372c30-6 40-40 60-40s20 30 40 30 16-22 36-22 18 26 40 26 22-12 44-10" stroke="#D5DCE5" stroke-width="2"/>
<!-- satellite orbit -->
<circle cx="560" cy="96" r="62" stroke="#D5DCE5" stroke-width="1.6" stroke-dasharray="3 6"/>
<g class="spin" style="transform-origin:560px 96px;animation-duration:14s"><g transform="translate(560,96)"><rect x="52" y="-7" width="18" height="14" rx="3" fill="#044978"/><path d="M48 0h-12M74 0h12" stroke="#0A777F" stroke-width="3.5"/></g></g>
<text x="360" y="462" text-anchor="middle" font-size="13" fill="#5B6B82">instruments for space, from the stratosphere to orbit</text>
</svg>""",
"cdh": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<!-- CT gantry -->
<circle cx="170" cy="240" r="110" fill="#F3F7FA" stroke="#044978" stroke-width="3"/>
<circle cx="170" cy="240" r="62" fill="#FFFFFF" stroke="#D5DCE5" stroke-width="2"/>
<g class="spin" style="transform-origin:170px 240px;animation-duration:9s"><path d="M170 130a110 110 0 0 1 95 55" stroke="#0A777F" stroke-width="10"/><circle cx="170" cy="130" r="8" fill="#3BA995"/></g>
<path d="M120 380h100" stroke="#044978" stroke-width="6"/>
<text x="170" y="410" text-anchor="middle" font-size="12" fill="#5B6B82">medical imaging</text>
<!-- reconstructed slice -->
<g class="card"><rect x="320" y="140" width="130" height="130" rx="10" fill="#0E2036"/></g>
<ellipse cx="385" cy="205" rx="50" ry="44" fill="#D5DCE5"/><ellipse cx="385" cy="205" rx="43" ry="37" fill="#5B6B82"/><ellipse cx="385" cy="205" rx="36" ry="30" fill="#F3F7FA" opacity=".85"/><path d="M385 178v54" stroke="#5B6B82" stroke-width="1.4"/><ellipse cx="379" cy="204" rx="4" ry="9" fill="#5B6B82"/><ellipse cx="391" cy="204" rx="4" ry="9" fill="#5B6B82"/>
<text x="385" y="290" text-anchor="middle" font-size="12" fill="#5B6B82">reconstruction with learning</text>
<path d="M282 240h30" stroke="#0A777F" stroke-width="3" class="flow"/>
<!-- data platform -->
<g class="card"><rect x="500" y="60" width="180" height="110" rx="14" fill="#044978"/></g>
<text x="590" y="94" text-anchor="middle" font-size="14" font-weight="600" fill="#FFFFFF">clinical data platform</text>
<g stroke="#3BA995" stroke-width="2.4"><path d="M520 118h140M520 136h100M520 154h120"/></g>
<path d="M450 205L500 140" stroke="#0A777F" stroke-width="2.6" stroke-dasharray="5 8" class="flow"/>
<!-- wearable and ECG -->
<g class="card"><rect x="520" y="250" width="70" height="90" rx="14" fill="#FFFFFF" stroke="#044978" stroke-width="3"/></g>
<rect x="532" y="262" width="46" height="66" rx="6" fill="#F3F7FA"/>
<path d="M538 300h8l5-14 8 26 7-18 5 6h9" stroke="#3BA995" stroke-width="2.2"/>
<path d="M590 300h90" stroke="#D5DCE5" stroke-width="2"/>
<path class="trace" pathLength="100" d="M594 300h14l8-22 10 44 10-32 8 10h30" stroke="#3BA995" stroke-width="2.6"/>
<path d="M555 250V170" stroke="#0A777F" stroke-width="2.6" stroke-dasharray="5 8" class="flow slow"/>
<text x="600" y="372" text-anchor="middle" font-size="12" fill="#5B6B82">wearables and remote monitoring</text>
<text x="360" y="462" text-anchor="middle" font-size="13" fill="#5B6B82">imaging, sensing, and the platform that keeps the data safe</text>
</svg>""",
"cei": """<svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect width="720" height="480" fill="#FFFFFF"/>
<!-- ground -->
<path d="M40 420h640" stroke="#D5DCE5" stroke-width="3"/>
<!-- turbine -->
<path d="M200 420V200" stroke="#044978" stroke-width="8"/>
<path d="M186 420h28" stroke="#044978" stroke-width="6"/>
<g class="spin" style="transform-origin:200px 200px;animation-duration:8s">
  <path d="M200 200l-8-120h16zM200 200l104 60-8 14zM200 200l-104 60 8 14z" fill="#0A777F"/>
  <g fill="#3BA995"><circle cx="200" cy="120" r="5" class="pulse"/><circle cx="270" cy="240" r="5" class="pulse" style="animation-delay:.7s"/><circle cx="130" cy="240" r="5" class="pulse" style="animation-delay:1.4s"/></g>
</g>
<circle cx="200" cy="200" r="16" fill="#FFFFFF" stroke="#044978" stroke-width="5"/>
<text x="200" y="450" text-anchor="middle" font-size="12" fill="#5B6B82">blade sensors, acoustic and vibration</text>
<!-- inspection drone -->
<g transform="translate(330,100)">
  <rect x="34" y="18" width="34" height="18" rx="5" fill="#044978"/>
  <path d="M18 8v10M84 8v10M18 18h16M84 18H68" stroke="#044978" stroke-width="2.4"/>
  <g stroke="#3BA995" stroke-width="2.6" class="spin" style="transform-origin:18px 8px"><path d="M2 8h32"/></g>
  <g stroke="#3BA995" stroke-width="2.6" class="spin" style="transform-origin:84px 8px"><path d="M68 8h32"/></g>
</g>
<path d="M381 136L292 180" stroke="#3BA995" stroke-width="2.4" stroke-dasharray="5 8" class="flow"/>
<text x="381" y="90" text-anchor="middle" font-size="12" fill="#5B6B82">drone inspection</text>
<!-- vibration signature -->
<g class="card"><rect x="440" y="150" width="240" height="150" rx="14" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<text x="560" y="176" text-anchor="middle" font-size="13" font-weight="600" fill="#0E2036">vibration signature</text>
<path d="M460 240h200" stroke="#D5DCE5" stroke-width="1.6"/>
<path class="trace" pathLength="100" d="M460 240c8-30 12-30 20 0s12 30 20 0 12-30 20 0 12 60 20 0 12-30 20 0 12 30 20 0 12-30 20 0 12 30 20 0 12-30 20 0 12 30 20 0" stroke="#0A777F" stroke-width="2.4"/>
<circle cx="540" cy="200" r="5" fill="#E25555" class="pulse"/>
<text x="600" y="286" text-anchor="end" font-size="11.5" fill="#5B6B82">anomaly at the blade root</text>
<!-- solar and hydrogen: the energy side -->
<g class="card"><rect x="480" y="320" width="90" height="60" rx="8" fill="#044978"/></g>
<g stroke="#FFFFFF" stroke-width="1.2" opacity=".6"><path d="M480 340h90M480 360h90M510 320v60M540 320v60"/></g>
<g class="card"><rect x="590" y="320" width="90" height="60" rx="8" fill="#FFFFFF" stroke="#0A777F" stroke-width="2"/></g>
<text x="635" y="356" text-anchor="middle" font-size="15" font-weight="700" fill="#0A777F">H2</text>
<text x="580" y="402" text-anchor="middle" font-size="12" fill="#5B6B82">generation, storage, and sustainability</text>
</svg>""",
}
LAB_ART = {k: theme_svg(v) for k, v in LAB_ART.items()}


HERO_ART = {
"grid": """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
  <marker id="arb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#044978"/></marker>
</defs><rect x="0" y="0" width="1200" height="600" fill="url(#sky)"/>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">THE PHYSICAL GRID</text><text x="470" y="52">THE MEASUREMENT PATH</text><text x="880" y="52">CONTROL AND DEFENSE</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h330M880 68h260"/></g>
<!-- towers and conductors -->
<g stroke="#044978" stroke-width="3.2">
  <path d="M120 470l18-250h20l18 250M126 400h44M132 340h32M138 285h20M96 400h88M104 340h72M114 285h52"/>
  <path d="M400 470l18-250h20l18 250M406 400h44M412 340h32M418 285h20M376 400h88M384 340h72M394 285h52"/>
</g>
<path d="M158 285Q279 355 418 285M114 340Q279 420 394 340" stroke="#D5DCE5" stroke-width="3"/>
<path class="flow" d="M158 285Q279 355 418 285" stroke="#0A777F" stroke-width="3.4"/>
<path class="flow slow" d="M114 340Q279 420 394 340" stroke="#0A777F" stroke-width="3.4"/>
<!-- substation -->
<g class="card"><rect x="196" y="418" width="164" height="54" rx="8" fill="#044978"/></g>
<g stroke="#FFFFFF" stroke-width="1.6" opacity=".55"><path d="M228 424v42M262 424v42M296 424v42M330 424v42M196 445h164"/></g>
<text x="278" y="500" text-anchor="middle" font-size="14" fill="#5B6B82">substation and feeder</text>
<!-- meters -->
<g class="card" fill="#FFFFFF" stroke="#044978" stroke-width="2"><rect x="128" y="120" width="60" height="62" rx="10"/><rect x="248" y="120" width="60" height="62" rx="10"/><rect x="368" y="120" width="60" height="62" rx="10"/></g>
<g stroke="#0A777F" stroke-width="2.4"><path d="M142 162a16 16 0 0 1 32 0M262 162a16 16 0 0 1 32 0M382 162a16 16 0 0 1 32 0"/><path d="M158 162l8-11M278 162l9-12M398 162l7-13"/></g>
<g fill="#5B6B82" font-size="13" text-anchor="middle"><text x="158" y="108">meter</text><text x="278" y="108">PMU</text><text x="398" y="108">meter</text></g>
<g stroke="#D5DCE5" stroke-width="2.4"><path d="M158 182v236M278 182v236M398 182v236"/></g>
<g stroke="#3BA995" stroke-width="3"><path class="flow" d="M158 418V182"/><path class="flow slow" d="M278 418V182"/><path class="flow" d="M398 418V182"/></g>
<!-- attack on the measurement path -->
<g class="pulse"><path d="M470 150l-46 30 24 6-30 40" stroke="#E25555" stroke-width="3.4"/><circle cx="418" cy="226" r="7" fill="#E25555"/></g>
<text x="470" y="132" font-size="14" fill="#E25555">false data injection</text>
<!-- network core -->
<g class="card"><circle cx="620" cy="300" r="96" fill="#FFFFFF" stroke="#044978" stroke-width="2"/></g>
<circle cx="620" cy="300" r="96" fill="none" stroke="#0A777F" stroke-width="3.4" class="flow slow"/>
<g stroke="#D5DCE5" stroke-width="1.4"><path d="M620 204v192M537 252l166 96M537 348l166-96"/></g>
<g fill="#044978"><circle cx="620" cy="204" r="7"/><circle cx="703" cy="252" r="7"/><circle cx="703" cy="348" r="7"/><circle cx="620" cy="396" r="7"/><circle cx="537" cy="348" r="7"/><circle cx="537" cy="252" r="7"/></g>
<circle cx="620" cy="300" r="18" fill="#0A777F"/><circle cx="620" cy="300" r="7" fill="#FFFFFF"/>
<text x="620" y="180" text-anchor="middle" font-size="14" fill="#5B6B82">utility communication network</text>
<text x="586" y="440" text-anchor="middle" font-size="14" fill="#5B6B82">observability-aware routing</text>
<!-- meter to core -->
<g stroke="#D5DCE5" stroke-width="2.4"><path d="M428 151C500 151 470 240 528 268M428 300h92M428 449C500 449 470 360 528 332"/></g>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M428 151C500 151 470 240 528 268"/><path class="flow slow" d="M428 300h92"/><path class="flow" d="M428 449C500 449 470 360 528 332"/></g>
<!-- defense stack -->
<g class="card"><rect x="880" y="110" width="260" height="250" rx="16" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<rect x="880" y="110" width="260" height="52" rx="16" fill="#044978"/><rect x="880" y="140" width="260" height="22" fill="#044978"/>
<text x="1010" y="143" text-anchor="middle" font-size="17" font-weight="600" fill="#FFFFFF">detection and control</text>
<g fill="#F3F7FA" stroke="#D5DCE5"><rect x="900" y="182" width="220" height="44" rx="9"/><rect x="900" y="238" width="220" height="44" rx="9"/><rect x="900" y="294" width="220" height="44" rx="9"/></g>
<g stroke="#0A777F" stroke-width="2.4" fill="none">
  <path d="M916 214l10-14 8 9 9-17 8 11"/>
  <circle cx="932" cy="260" r="13"/><path d="M932 251v9l7 6"/>
  <path d="M916 322l9-9 7 7 13-15M948 305h-7v7"/>
</g>
<g font-size="14.5" fill="#0E2036"><text x="962" y="209">false data detection</text><text x="962" y="265">state estimation</text><text x="962" y="321">restoration planning</text></g>
<g fill="#3BA995"><circle cx="1104" cy="204" r="5" class="pulse"/><circle cx="1104" cy="260" r="5" class="pulse" style="animation-delay:1s"/><circle cx="1104" cy="316" r="5" class="pulse" style="animation-delay:2s"/></g>
<!-- shield and control return -->
<path d="M760 92l44 15v38c0 31-19 51-44 62-25-11-44-31-44-62v-38z" fill="#3BA995"/>
<path d="M739 142l13 13 29-31" stroke="#FFFFFF" stroke-width="7"/>
<text x="760" y="212" text-anchor="middle" font-size="13.5" fill="#5B6B82">verified measurements</text>
<path d="M726 290h144" stroke="#0A777F" stroke-width="3" marker-end="url(#ar)"/>
<text x="816" y="276" text-anchor="middle" font-size="13.5" fill="#5B6B82">telemetry</text>
<path d="M880 392H620v-4" stroke="#3BA995" stroke-width="3" stroke-dasharray="7 9" marker-end="url(#arg)"/>
<text x="780" y="418" text-anchor="middle" font-size="13.5" fill="#5B6B82">control action</text>
<path d="M60 540h1080" stroke="#D5DCE5" stroke-width="1.4"/>
<text x="600" y="572" text-anchor="middle" font-size="15" fill="#5B6B82">sense at the meter, carry it over the network, decide in the control room, act on the breaker</text>
</svg>""",
"ai": """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
  <marker id="arb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#044978"/></marker>
</defs><rect x="0" y="0" width="1200" height="600" fill="url(#sky)"/>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">OBSERVATIONS</text><text x="470" y="52">MODEL AND ENFORCEMENT</text><text x="880" y="52">PHYSICAL PLANT</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h330M880 68h260"/></g>
<!-- federated sites -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5"><rect x="60" y="110" width="200" height="110" rx="12"/><rect x="60" y="248" width="200" height="110" rx="12"/><rect x="60" y="386" width="200" height="110" rx="12"/></g>
<g font-size="15" font-weight="600" fill="#0E2036"><text x="84" y="142">Utility A</text><text x="84" y="280">Utility B</text><text x="84" y="418">Utility C</text></g>
<g font-size="13" fill="#5B6B82"><text x="84" y="162">local data stays local</text><text x="84" y="300">local data stays local</text><text x="84" y="438">local data stays local</text></g>
<g stroke="#0A777F" stroke-width="2.2"><path d="M84 186h40v18h-40zM134 186h40v18h-40zM184 186h40v18h-40z"/><path d="M84 324h40v18h-40zM134 324h40v18h-40zM184 324h40v18h-40z"/><path d="M84 462h40v18h-40zM134 462h40v18h-40zM184 462h40v18h-40z"/></g>
<!-- gradients up, model down -->
<g stroke="#D5DCE5" stroke-width="2.4"><path d="M260 165C340 165 330 250 400 262M260 303h140M260 441C340 441 330 356 400 344"/></g>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M260 165C340 165 330 250 400 262"/><path class="flow slow" d="M260 303h140"/><path class="flow" d="M260 441C340 441 330 356 400 344"/></g>
<text x="330" y="150" text-anchor="middle" font-size="13" fill="#5B6B82">model updates only</text>
<!-- the network -->
<g class="card"><rect x="400" y="150" width="300" height="306" rx="16" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<g stroke="#D5DCE5" stroke-width="1.3">
  <path d="M452 220L520 190M452 220L520 250M452 220L520 310M452 303L520 190M452 303L520 250M452 303L520 310M452 303L520 370M452 386L520 250M452 386L520 310M452 386L520 370M528 190L596 250M528 250L596 250M528 310L596 310M528 370L596 310M528 250L596 310M528 310L596 250"/>
</g>
<g stroke="#0A777F" stroke-width="2.2"><path class="flow" d="M452 220L520 190L596 250"/><path class="flow slow" d="M452 386L520 310L596 310"/></g>
<g fill="#044978"><circle cx="452" cy="220" r="10"/><circle cx="452" cy="303" r="10"/><circle cx="452" cy="386" r="10"/><circle cx="520" cy="190" r="10"/><circle cx="520" cy="250" r="10"/><circle cx="520" cy="310" r="10"/><circle cx="520" cy="370" r="10"/></g>
<g fill="#0A777F"><circle cx="596" cy="250" r="11"/><circle cx="596" cy="310" r="11"/></g>
<text x="550" y="490" text-anchor="middle" font-size="14" fill="#5B6B82">federated model, grounded in the physics of the plant</text>
<!-- safety gate -->
<path d="M620 280h46" stroke="#D5DCE5" stroke-width="2.4"/><path class="flow" d="M620 280h46" stroke="#0A777F" stroke-width="3"/>
<g class="card"><rect x="700" y="228" width="150" height="150" rx="18" fill="#3BA995"/></g>
<path d="M740 300l18 20 42-46" stroke="#FFFFFF" stroke-width="9"/>
<text x="775" y="408" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">safety enforcement</text>
<text x="775" y="430" text-anchor="middle" font-size="13" fill="#5B6B82">every action checked before it reaches the plant</text>
<!-- plant -->
<path d="M850 300h50" stroke="#D5DCE5" stroke-width="2.4"/><path class="flow" d="M850 300h50" stroke="#3BA995" stroke-width="3" marker-end="url(#arg)"/>
<g class="card"><circle cx="1010" cy="290" r="94" fill="#F3F7FA" stroke="#D5DCE5"/></g>
<g class="spin" style="transform-origin:1010px 290px"><path d="M1010 290l-11-70 22 0zM1010 290l60 38-11 19zM1010 290l-60 38 11 19z" fill="#044978"/></g>
<circle cx="1010" cy="290" r="14" fill="#FFFFFF" stroke="#044978" stroke-width="4"/>
<g stroke="#044978" stroke-width="3"><path d="M1010 384v66M970 450h80"/></g>
<text x="1010" y="486" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">generation, storage, and load</text>
<!-- feedback -->
<path d="M1010 512V540H160v-44" stroke="#3BA995" stroke-width="2.6" stroke-dasharray="7 9" class="flow slow" marker-end="url(#arg)"/>
<text x="600" y="572" text-anchor="middle" font-size="15" fill="#5B6B82">measurements return, the model updates, the enforcement layer never moves</text>
</svg>""",
"fiber": """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
  <marker id="arb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#044978"/></marker>
</defs><rect x="0" y="0" width="1200" height="600" fill="url(#sky)"/>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">FIBER AND BANDS</text><text x="470" y="52">IMPAIRMENT-AWARE ALLOCATION</text><text x="880" y="52">SERVICES</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h330M880 68h260"/></g>
<!-- fiber cross-section -->
<g class="card"><circle cx="170" cy="250" r="110" fill="#FFFFFF" stroke="#044978" stroke-width="2.4"/></g>
<circle cx="170" cy="250" r="74" stroke="#D5DCE5" stroke-width="1.6"/>
<g fill="#0A777F"><circle cx="170" cy="250" r="14"/><circle cx="134" cy="214" r="10"/><circle cx="206" cy="214" r="10"/><circle cx="134" cy="286" r="10"/><circle cx="206" cy="286" r="10"/><circle cx="170" cy="196" r="10"/><circle cx="170" cy="304" r="10"/></g>
<circle cx="170" cy="250" r="26" fill="#3BA995" opacity=".3" class="pulse"/>
<text x="170" y="394" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">multi-core fiber</text>
<text x="170" y="416" text-anchor="middle" font-size="13" fill="#5B6B82">space-division multiplexing</text>
<!-- amplified span -->
<path d="M290 250h160" stroke="#044978" stroke-width="3.4"/>
<g fill="#FFFFFF" stroke="#044978" stroke-width="2.4"><path d="M352 228l34 22-34 22z"/></g>
<path class="flow" d="M290 250h160" stroke="#0A777F" stroke-width="3.4"/>
<text x="370" y="212" text-anchor="middle" font-size="13" fill="#5B6B82">amplified span</text>
<!-- spectrum -->
<path d="M470 470h420" stroke="#5B6B82" stroke-width="1.8"/>
<g stroke="#D5DCE5" stroke-width="1.2"><path d="M470 470V150M890 470V150"/></g>
<rect x="482" y="330" width="86" height="140" rx="4" fill="#044978" class="grow" style="transform-origin:525px 470px"/>
<rect x="576" y="270" width="60" height="200" rx="4" fill="#0A777F" class="grow" style="transform-origin:606px 470px;animation-delay:.4s"/>
<rect x="644" y="360" width="70" height="110" rx="4" fill="#3BA995" class="grow" style="transform-origin:679px 470px;animation-delay:.8s"/>
<rect x="722" y="240" width="94" height="230" rx="4" fill="#044978" class="grow" style="transform-origin:769px 470px;animation-delay:1.2s"/>
<rect x="824" y="330" width="56" height="140" rx="4" fill="#0A777F" class="grow" style="transform-origin:852px 470px;animation-delay:1.6s"/>
<path d="M470 452C560 446 640 436 730 420S850 396 890 380" stroke="#E25555" stroke-width="3" stroke-dasharray="8 10"/>
<text x="890" y="524" text-anchor="end" font-size="14" fill="#E25555">nonlinear interference grows with load</text>
<g font-size="14" fill="#5B6B82" text-anchor="middle"><text x="525" y="494">S band</text><text x="606" y="494">C band</text><text x="679" y="494">C band</text><text x="769" y="494">L band</text><text x="852" y="494">L band</text></g>
<g font-size="12.5" fill="#0E2036" text-anchor="middle" font-weight="600"><text x="525" y="316">16QAM</text><text x="606" y="256">QPSK</text><text x="679" y="346">8QAM</text><text x="769" y="226">64QAM</text><text x="852" y="316">16QAM</text></g>
<text x="680" y="130" text-anchor="middle" font-size="14" fill="#5B6B82">each lightpath gets its own width, format, core, and power</text>
<!-- services -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5"><rect x="930" y="150" width="210" height="80" rx="12"/><rect x="930" y="248" width="210" height="80" rx="12"/><rect x="930" y="346" width="210" height="80" rx="12"/></g>
<g stroke="#044978" stroke-width="2.6"><path d="M960 190h-1M956 176h48v28h-48z"/><path d="M956 274h48v28h-48zM968 288h24"/><path d="M980 402v-30M962 372h36"/></g>
<g font-size="15" font-weight="600" fill="#0E2036"><text x="1020" y="184">6G fronthaul</text><text x="1020" y="282">data centers</text><text x="1020" y="380">science flows</text></g>
<g font-size="12.5" fill="#5B6B82"><text x="1020" y="204">latency class</text><text x="1020" y="302">capacity class</text><text x="1020" y="400">scheduled circuits</text></g>
<g stroke="#0A777F" stroke-width="2.6"><path class="flow" d="M890 210h34" marker-end="url(#ar)"/><path class="flow slow" d="M890 288h34" marker-end="url(#ar)"/><path class="flow" d="M890 386h34" marker-end="url(#ar)"/></g>
<text x="600" y="572" text-anchor="middle" font-size="15" fill="#5B6B82">more spectrum and more cores, provisioned so the physics still holds</text>
</svg>""",
"edge": """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
  <marker id="arb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#044978"/></marker>
</defs><rect x="0" y="0" width="1200" height="600" fill="url(#sky)"/>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">REPLICATED EDGE CLUSTER</text><text x="470" y="52">AGREEMENT UNDER FAULT</text><text x="880" y="52">WHAT IT CONTROLS</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h330M880 68h260"/></g>
<!-- replicas -->
<g stroke="#D5DCE5" stroke-width="1.8"><path d="M210 190L420 140M210 190L330 330M210 190L360 420M420 140L330 330M420 140L560 250M330 330L360 420M330 330L560 250M360 420L560 250"/></g>
<g stroke="#0A777F" stroke-width="2.8"><path class="flow" d="M210 190L420 140"/><path class="flow slow" d="M330 330L560 250"/><path class="flow" d="M210 190L330 330"/></g>
<g class="card" fill="#FFFFFF" stroke="#044978" stroke-width="2.4">
  <rect x="150" y="160" width="120" height="62" rx="12"/><rect x="360" y="110" width="120" height="62" rx="12"/><rect x="270" y="300" width="120" height="62" rx="12"/>
</g>
<g stroke="#3BA995" stroke-width="3.4"><path d="M178 192l13 13 24-26M388 142l13 13 24-26M298 332l13 13 24-26"/></g>
<g font-size="13" fill="#5B6B82" text-anchor="middle"><text x="210" y="244">replica</text><text x="420" y="194">replica</text><text x="330" y="384">replica</text></g>
<!-- faulty replica -->
<g class="pulse"><rect x="300" y="390" width="120" height="62" rx="12" fill="#FDECEC" stroke="#E25555" stroke-width="2.4"/><path d="M336 410l24 24M360 410l-24 24" stroke="#E25555" stroke-width="4"/></g>
<text x="446" y="428" text-anchor="start" font-size="13" fill="#E25555">crashed or lying</text>
<!-- quorum -->
<g class="card"><circle cx="620" cy="250" r="66" fill="#FFFFFF" stroke="#0A777F" stroke-width="2.6"/></g>
<text x="620" y="244" text-anchor="middle" font-size="17" font-weight="600" fill="#0A777F">quorum</text>
<text x="620" y="268" text-anchor="middle" font-size="13.5" fill="#5B6B82">3 of 4 agree</text>
<text x="620" y="356" text-anchor="middle" font-size="14" fill="#5B6B82">the decision survives the fault</text>
<!-- mobile edge -->
<g transform="translate(140,462)">
  <rect x="42" y="20" width="44" height="22" rx="6" fill="#044978"/>
  <path d="M20 8v12M108 8v12M20 20h22M108 20H86" stroke="#044978" stroke-width="2.6"/>
  <g stroke="#0A777F" stroke-width="3" class="spin" style="transform-origin:20px 8px"><path d="M0 8h40"/></g>
  <g stroke="#0A777F" stroke-width="3" class="spin" style="transform-origin:108px 8px"><path d="M88 8h40"/></g>
</g>
<text x="204" y="540" text-anchor="middle" font-size="13.5" fill="#5B6B82">aerial and satellite edge, intermittently connected</text>
<circle cx="470" cy="516" r="8" fill="#3BA995"/>
<path d="M268 492C336 480 404 498 462 512" stroke="#3BA995" stroke-width="2.6" stroke-dasharray="6 8" class="flow slow"/>
<!-- controlled systems -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5"><rect x="880" y="120" width="260" height="120" rx="14"/><rect x="880" y="262" width="260" height="120" rx="14"/></g>
<g stroke="#044978" stroke-width="2.6"><path d="M916 196V150l24-14 24 14v46M916 196h48M926 166h28"/></g>
<text x="1000" y="164" font-size="16" font-weight="600" fill="#0E2036">grid controllers</text>
<text x="1000" y="188" font-size="13" fill="#5B6B82">real-time deadlines</text>
<g stroke="#0A777F" stroke-width="2.6"><rect x="912" y="300" width="56" height="44" rx="6"/><path d="M924 322h32M940 306v32"/></g>
<text x="1000" y="306" font-size="16" font-weight="600" fill="#0E2036">digital twins</text>
<text x="1000" y="330" font-size="13" fill="#5B6B82">served from hybrid clouds</text>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M690 210h182" marker-end="url(#ar)"/><path class="flow slow" d="M690 300h182" marker-end="url(#ar)"/></g>
<text x="600" y="572" text-anchor="middle" font-size="15" fill="#5B6B82">consensus fast enough for a control loop, correct even when a replica misbehaves</text>
</svg>""",
"chip": """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
  <marker id="arb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#044978"/></marker>
</defs><rect x="0" y="0" width="1200" height="600" fill="url(#sky)"/>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">SILICON AND FIRMWARE</text><text x="470" y="52">EVIDENCE</text><text x="880" y="52">VERIFIER AND SCALE</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h330M880 68h260"/></g>
<!-- die -->
<g class="card"><rect x="110" y="150" width="270" height="270" rx="16" fill="#044978"/></g>
<rect x="168" y="208" width="154" height="154" rx="10" fill="#0A777F"/>
<g stroke="#044978" stroke-width="4">
  <path d="M152 150v-34M196 150v-34M240 150v-34M284 150v-34M328 150v-34M152 420v34M196 420v34M240 420v34M284 420v34M328 420v34"/>
  <path d="M110 190H76M110 236H76M110 282H76M110 328H76M110 374H76M380 190h34M380 236h34M380 282h34M380 328h34M380 374h34"/>
</g>
<rect x="222" y="268" width="46" height="38" rx="5" fill="#FFFFFF"/>
<path d="M231 268v-12a14 14 0 0 1 28 0v12" stroke="#FFFFFF" stroke-width="5"/>
<text x="245" y="486" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">attested device</text>
<text x="245" y="508" text-anchor="middle" font-size="13" fill="#5B6B82">trojan-checked at RTL, measured at boot</text>
<!-- counters -->
<path d="M414 282h56" stroke="#D5DCE5" stroke-width="2.6"/><path class="flow" d="M414 282h56" stroke="#0A777F" stroke-width="3.2"/>
<path d="M490 470h300" stroke="#5B6B82" stroke-width="1.8"/>
<rect x="506" y="330" width="26" height="140" fill="#0A777F" class="grow" style="transform-origin:519px 470px"/>
<rect x="548" y="270" width="26" height="200" fill="#0A777F" class="grow" style="transform-origin:561px 470px;animation-delay:.3s"/>
<rect x="590" y="360" width="26" height="110" fill="#0A777F" class="grow" style="transform-origin:603px 470px;animation-delay:.6s"/>
<rect x="632" y="240" width="26" height="230" fill="#0A777F" class="grow" style="transform-origin:645px 470px;animation-delay:.9s"/>
<rect x="674" y="320" width="26" height="150" fill="#0A777F" class="grow" style="transform-origin:687px 470px;animation-delay:1.2s"/>
<g class="pulse"><rect x="716" y="408" width="26" height="62" fill="#E25555"/><circle cx="729" cy="386" r="9" fill="#E25555"/></g>
<rect x="758" y="352" width="26" height="118" fill="#0A777F"/>
<text x="640" y="200" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">hardware performance counters</text>
<text x="640" y="222" text-anchor="middle" font-size="13" fill="#5B6B82">an outlier here is corruption that raised no error</text>
<text x="800" y="514" text-anchor="start" font-size="13.5" fill="#E25555">silent data corruption</text>
<path d="M745 386h48v122" stroke="#E25555" stroke-width="1.6" stroke-dasharray="4 5"/>
<text x="620" y="514" text-anchor="middle" font-size="13.5" fill="#5B6B82">cheap enough to leave running in production</text>
<!-- rack -->
<g class="card"><rect x="880" y="120" width="180" height="330" rx="12" fill="#FFFFFF" stroke="#044978" stroke-width="2.4"/></g>
<g stroke="#D5DCE5" stroke-width="1.6"><path d="M880 176h180M880 232h180M880 288h180M880 344h180M880 400h180"/></g>
<g fill="#3BA995"><circle cx="1036" cy="148" r="5" class="pulse"/><circle cx="1036" cy="204" r="5" class="pulse" style="animation-delay:.6s"/><circle cx="1036" cy="260" r="5" class="pulse" style="animation-delay:1.2s"/><circle cx="1036" cy="316" r="5" class="pulse" style="animation-delay:1.8s"/><circle cx="1036" cy="372" r="5" class="pulse" style="animation-delay:2.4s"/><circle cx="1036" cy="428" r="5" class="pulse" style="animation-delay:3s"/></g>
<g stroke="#0A777F" stroke-width="2.2"><path d="M900 148h60M900 204h48M900 260h66M900 316h54M900 372h60M900 428h42"/></g>
<text x="970" y="486" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">HPC and parallel I/O</text>
<text x="970" y="508" text-anchor="middle" font-size="13" fill="#5B6B82">data-intensive science at scale</text>
<path d="M800 282h72" stroke="#0A777F" stroke-width="3" marker-end="url(#ar)"/>
<text x="600" y="572" text-anchor="middle" font-size="15" fill="#5B6B82">trust the answer only if you can check the hardware that produced it</text>
</svg>""",
"health": """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round"><defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
  <marker id="arb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#044978"/></marker>
</defs><rect x="0" y="0" width="1200" height="600" fill="url(#sky)"/>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">TRANSPORTATION</text><text x="470" y="52">STRUCTURES</text><text x="880" y="52">HEALTH AND FACILITIES</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h330M880 68h260"/></g>
<!-- road -->
<g class="card"><rect x="60" y="286" width="330" height="76" rx="8" fill="#F3F7FA" stroke="#D5DCE5"/></g>
<path class="flow slow" d="M72 344h306" stroke="#5B6B82" stroke-width="2.4" stroke-dasharray="20 16"/>
<g transform="translate(0,26)"><path d="M96 300h104l-18-30H114z" fill="#044978"/><path d="M86 300h124v14H86z" fill="#044978" opacity=".85"/><circle cx="114" cy="318" r="10" fill="#FFFFFF" stroke="#044978" stroke-width="3"/><circle cx="182" cy="318" r="10" fill="#FFFFFF" stroke="#044978" stroke-width="3"/></g>
<g transform="translate(0,26)"><path d="M248 300h104l-18-30H266z" fill="#0A777F"/><path d="M238 300h124v14H238z" fill="#0A777F" opacity=".85"/><circle cx="266" cy="318" r="10" fill="#FFFFFF" stroke="#0A777F" stroke-width="3"/><circle cx="334" cy="318" r="10" fill="#FFFFFF" stroke="#0A777F" stroke-width="3"/></g>
<path d="M196 264q54-56 108 0" stroke="#3BA995" stroke-width="3" stroke-dasharray="5 8" class="flow"/>
<g stroke="#3BA995" stroke-width="2.6" class="pulse"><path d="M148 268v-20M138 258l10-10 10 10M300 268v-20M290 258l10-10 10 10"/></g>
<text x="225" y="416" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">connected and automated vehicles</text>
<text x="225" y="438" text-anchor="middle" font-size="13" fill="#5B6B82">trajectory prediction, roadway assessment</text>
<!-- bridge -->
<g stroke="#044978" stroke-width="3.2">
  <path d="M450 420h300M490 420V290M710 420V290M450 290h300"/>
  <path d="M490 290q110-104 220 0"/>
</g>
<g stroke="#D5DCE5" stroke-width="1.8"><path d="M540 420V252M600 420V232M660 420V252"/></g>
<g fill="#3BA995"><circle cx="540" cy="252" r="8" class="pulse"/><circle cx="600" cy="232" r="8" class="pulse" style="animation-delay:.7s"/><circle cx="660" cy="252" r="8" class="pulse" style="animation-delay:1.4s"/></g>
<g transform="translate(466,140)">
  <rect x="34" y="18" width="34" height="18" rx="5" fill="#0A777F"/>
  <path d="M18 8v10M84 8v10M18 18h16M84 18H68" stroke="#0A777F" stroke-width="2.4"/>
  <g stroke="#3BA995" stroke-width="2.6" class="spin" style="transform-origin:18px 8px"><path d="M2 8h32"/></g>
  <g stroke="#3BA995" stroke-width="2.6" class="spin" style="transform-origin:84px 8px"><path d="M68 8h32"/></g>
</g>
<path d="M517 180v46" stroke="#3BA995" stroke-width="2.4" stroke-dasharray="5 8" class="flow"/>
<text x="600" y="466" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">structural health monitoring</text>
<text x="600" y="488" text-anchor="middle" font-size="13" fill="#5B6B82">blades, bridges, and buildings, inspected from the air</text>
<!-- hospital and reactor -->
<g class="card"><rect x="820" y="120" width="150" height="130" rx="14" fill="#0A777F"/></g>
<path d="M895 152v66M862 185h66" stroke="#FFFFFF" stroke-width="10"/>
<path d="M984 196h20l12-36 18 72 16-52 12 16h22" stroke="#3BA995" stroke-width="3"/>
<text x="895" y="278" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">digital health</text>
<text x="895" y="300" text-anchor="middle" font-size="13" fill="#5B6B82">imaging and clinical platforms</text>
<g class="card"><path d="M1020 450V376a60 60 0 0 1 120 0v74z" fill="#FFFFFF" stroke="#044978" stroke-width="2.4"/></g>
<path d="M1020 396h120" stroke="#D5DCE5" stroke-width="1.8"/>
<circle cx="1080" cy="412" r="26" stroke="#0A777F" stroke-width="3"/>
<circle cx="1080" cy="412" r="8" fill="#0A777F"/>
<g stroke="#3BA995" stroke-width="2.6"><path d="M1080 386a26 26 0 0 1 23 39M1080 438a26 26 0 0 1-23-39"/></g>
<text x="1080" y="490" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">nuclear security</text>
<text x="1080" y="512" text-anchor="middle" font-size="13" fill="#5B6B82">safeguards and robotics</text>
<path d="M820 200H700" stroke="#0A777F" stroke-width="2.6" stroke-dasharray="6 8" class="flow slow"/>
<text x="600" y="572" text-anchor="middle" font-size="15" fill="#5B6B82">one loop, four domains, each stressing it in a different way</text>
</svg>""",
}
HERO_ART["hpc"] = HERO_ART["chip"]
HERO_ART["nuclear"] = """<svg viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" font-family="IBM Plex Sans, Arial, sans-serif" fill="none" stroke-linecap="round" stroke-linejoin="round">
<rect width="1200" height="600" fill="url(#sky)"/>
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
<marker id="nar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker></defs>
<g font-size="15" font-weight="600" letter-spacing=".06em" fill="#5B6B82">
  <text x="60" y="52">THE FACILITY</text><text x="470" y="52">MEASUREMENT AND VERIFICATION</text><text x="880" y="52">SAFEGUARDS AND TRAINING</text></g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M60 68h330M470 68h360M880 68h260"/></g>
<!-- containment -->
<path d="M96 470V300a130 130 0 0 1 260 0v170z" fill="#FFFFFF" stroke="#044978" stroke-width="3.4"/>
<path d="M96 340h260" stroke="#D5DCE5" stroke-width="2"/>
<circle cx="226" cy="382" r="52" stroke="#0A777F" stroke-width="3.4"/>
<circle cx="226" cy="382" r="15" fill="#0A777F"/>
<g stroke="#3BA995" stroke-width="3.4"><path d="M226 330a52 52 0 0 1 45 78M226 434a52 52 0 0 1-45-78"/></g>
<text x="226" y="510" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">research reactor and fuel cycle</text>
<text x="226" y="532" text-anchor="middle" font-size="13" fill="#5B6B82">material accounting and containment</text>
<!-- robot going where people should not -->
<g transform="translate(60,108)">
  <rect x="0" y="30" width="86" height="42" rx="8" fill="#044978"/>
  <rect x="18" y="8" width="50" height="26" rx="6" fill="#0A777F"/>
  <circle cx="30" cy="21" r="5" fill="#FFFFFF"/><circle cx="56" cy="21" r="5" fill="#FFFFFF"/>
  <g stroke="#044978" stroke-width="4"><path d="M0 76h86"/></g>
  <circle cx="18" cy="82" r="10" fill="#FFFFFF" stroke="#044978" stroke-width="4"/>
  <circle cx="68" cy="82" r="10" fill="#FFFFFF" stroke="#044978" stroke-width="4"/>
</g>
<text x="103" y="224" text-anchor="middle" font-size="13" fill="#5B6B82">robotic inspection</text>
<!-- detector and counts -->
<g class="card"><rect x="430" y="330" width="86" height="130" rx="10" fill="#044978"/></g>
<rect x="446" y="346" width="54" height="66" rx="6" fill="#0A777F"/>
<circle cx="473" cy="436" r="6" fill="#3BA995" class="pulse"/>
<text x="473" y="486" text-anchor="middle" font-size="13.5" fill="#5B6B82">detector</text>
<g stroke="#3BA995" stroke-width="3" stroke-dasharray="3 10"><path class="flow" d="M290 382h132"/></g>
<!-- spectrum -->
<g class="card"><rect x="560" y="120" width="300" height="300" rx="16" fill="#FFFFFF" stroke="#D5DCE5"/></g>
<text x="710" y="152" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">gamma spectrum</text>
<path d="M590 380h240M590 380V180" stroke="#5B6B82" stroke-width="1.8"/>
<path d="M592 366c24-5 36-34 48-34s10 28 24 30 18-140 36-140 14 118 32 118 12-48 28-48 20 36 34 36 10-12 30-16" stroke="#D5DCE5" stroke-width="2.4"/>
<path class="trace" pathLength="100" d="M592 366c24-5 36-34 48-34s10 28 24 30 18-140 36-140 14 118 32 118 12-48 28-48 20 36 34 36 10-12 30-16" stroke="#0A777F" stroke-width="3"/>
<g fill="#3BA995"><circle cx="700" cy="222" r="6" class="pulse"/><circle cx="764" cy="304" r="5" class="pulse" style="animation-delay:.9s"/></g>
<text x="710" y="404" text-anchor="middle" font-size="13" fill="#5B6B82">isotopic signatures verified against declarations</text>
<!-- safeguards column -->
<g class="card" fill="#FFFFFF" stroke="#D5DCE5"><rect x="900" y="120" width="250" height="96" rx="12"/><rect x="900" y="240" width="250" height="96" rx="12"/><rect x="900" y="360" width="250" height="96" rx="12"/></g>
<text x="1025" y="156" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">facility security</text>
<text x="1025" y="180" text-anchor="middle" font-size="13" fill="#5B6B82">physical and cyber, with</text>
<text x="1025" y="200" text-anchor="middle" font-size="13" fill="#5B6B82">incident analysis</text>
<text x="1025" y="276" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">state energy policy</text>
<text x="1025" y="300" text-anchor="middle" font-size="13" fill="#5B6B82">Massachusetts nuclear and</text>
<text x="1025" y="320" text-anchor="middle" font-size="13" fill="#5B6B82">fusion energy roadmaps</text>
<text x="1025" y="396" text-anchor="middle" font-size="15" font-weight="600" fill="#0E2036">international training</text>
<text x="1025" y="420" text-anchor="middle" font-size="13" fill="#5B6B82">IAEA Intercontinental</text>
<text x="1025" y="440" text-anchor="middle" font-size="13" fill="#5B6B82">Nuclear Institute</text>
<g stroke="#0A777F" stroke-width="3"><path class="flow" d="M866 168h26" marker-end="url(#nar)"/><path class="flow slow" d="M866 288h26" marker-end="url(#nar)"/><path class="flow" d="M866 408h26" marker-end="url(#nar)"/></g>
<!-- shield -->
<path d="M356 92l40 14v34c0 28-17 46-40 56-23-10-40-28-40-56v-34z" fill="#3BA995"/>
<path d="M337 138l12 12 26-28" stroke="#FFFFFF" stroke-width="6.5"/>
<text x="356" y="218" text-anchor="middle" font-size="13" fill="#5B6B82">safeguards verified</text>
<path d="M60 560h1080" stroke="#D5DCE5" stroke-width="1.4"/>
<text x="600" y="588" text-anchor="middle" font-size="15" fill="#5B6B82">measure what is there, verify it against what was declared, and secure the facility that holds it</text>
</svg>"""
HERO_ART = {k: theme_svg(v) for k, v in HERO_ART.items()}



SCHEMATIC = theme_svg(SCHEMATIC)

METRICS = {}
_mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json")
if os.path.exists(_mp):
    METRICS = json.load(open(_mp))
LIVE_METRICS = False   # OpenAlex figures retired; citation numbers come from Google Scholar only

def metrics_slot(p):
    if p.get("inst", "Lowell") is None: return ""
    if LIVE_METRICS:
        return f'<div class="metrics" data-name="{esc(p["name"])}" data-inst="{esc(p.get("inst", "Lowell"))}" aria-live="polite"></div>'
    m = METRICS.get(p["name"])
    src = METRICS.get("_source", "")
    inner = ""
    if m:
        inner = (f'<span><b>{m["citations"]:,}</b> citations</span><span><b>{m["h"]}</b> h-index</span>'
                 f'<span><b>{m["works"]:,}</b> papers</span><span class="src" title="{esc(src)} data, {esc(METRICS.get("_date",""))}">{esc(src)}</span>')
    live = f' data-name="{esc(p["name"])}" data-inst="{esc(p.get("inst", "Lowell"))}"' if LIVE_METRICS else ""
    return f'<div class="metrics"{live} aria-live="polite">{inner}</div>'

def person_card(p, size="lg", with_photo=True):
    lines = []
    if with_photo:
        lines.append(avatar(p, size))
    tag = f' <span class="ptag">{esc(p["tag"])}</span>' if p.get("tag") else ''
    lines += [f'<h3>{esc(p["name"])}{tag}</h3>', f'<p class="ptitle">{esc(p["title"])}</p>']
    if p.get("title2"): lines.append(f'<p class="ptitle strong">{esc(p["title2"])}</p>')
    lines.append(f'<p class="pareas">{esc(p["areas"])}</p>')
    if p.get("role"):
        lines.append(f'<p class="prole">{esc(p["role"])}</p>')
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(f'<span>{esc(p["phone"])}</span>')
    if p.get("office"): meta.append(f'<span>{esc(p["office"])}</span>')
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">{"NYU profile" if "nyu.edu" in p["url"] else ("LinkedIn" if "linkedin.com" in p["url"] else "UMass Lowell profile")}</a>')
    if p.get("inst", "Lowell") is not None: meta += id_links(p["name"])
    lines.append('<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in meta) + '</p>')
    if scholar_line(p["name"]): lines.append('<p class="gsline">' + scholar_line(p["name"]) + '</p>')
    lines.append(metrics_slot(p))
    return '<article class="person">' + "".join(lines) + '</article>'

def person_row(p):
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(esc(p["phone"]))
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">{"LinkedIn" if "linkedin.com" in p["url"] else "Profile"}</a>')
    if p.get("inst", "Lowell") is not None: meta += id_links(p["name"])
    gs = ('<div class="gsline">' + scholar_line(p["name"]) + '</div>') if scholar_line(p["name"]) else ''
    tag = f'<span class="ptag">{esc(p["tag"])}</span>' if p.get("tag") else ''
    return ('<li class="prow">' + avatar(p, "sm") + '<div><span class="pname">' + esc(p["name"]) + tag + '</span><span class="ptitle2">' + esc(p["title"]) + '</span>'
            '<span class="pareas2">' + esc(p["areas"]) + '</span>'
            + (f'<span class="pnote">{esc(p["note"])}</span>' if p.get("note") else "")
            + '<div class="pcontact">' + "".join(f'<span class="ci">{m}</span>' for m in meta) + '</div>' + gs + metrics_slot(p) + '</div></li>')

# ---------------------------------------------------------------- counts
n_pubs = len(P)
n_journal = sum(1 for p in P if p["type"] == "journal")
n_faculty = 1 + len(FACULTY["core"]) + len(FACULTY["affiliated"])

def build():
    thrusts_html = "".join(
        f'<div class="thrust"><a class="art" href="research-{esc(i)}.html">{ART[i]}</a><div class="body"><h3><a href="research-{esc(i)}.html">{esc(t)}</a></h3><p>{esc(d)}</p><div class="who"><b>{esc(w.split(",")[0])}</b> leads{esc("; with " + w.split(", ", 1)[1] if ", " in w else "")}</div><p class="more2"><a href="research-{esc(i)}.html">More on this thrust</a></p></div></div>'
        for i, t, d, w in THRUSTS)

    _center = [canonical_person(p["name"]) for p in [FACULTY["director"]] + FACULTY["core"] + FACULTY["affiliated"]]
    _pi_counts = {p: sum(1 for pr in PROJECTS if p in {n for n, _ in project_people(pr)}) for p in _center}
    _pis = sorted(_center, key=lambda n: n.split()[-1])
    _yrs = sorted({y for pr in PROJECTS for y in project_years(pr)}, reverse=True)
    _thrusts = [(k, t) for k, t, _, _ in THRUSTS if any(project_thrust(pr) == k for pr in PROJECTS)]
    projfilters = (
        '<div class="pfilters" role="group" aria-label="Filter projects">'
        '<div class="frow"><span class="flab">Investigator</span>'
        '<button class="chip" data-f="pi" data-v="all" aria-pressed="true" type="button">All</button>'
        + '<div class="fchips">' + "".join(f'<button class="chip" data-f="pi" data-v="{esc(p)}" aria-pressed="false" type="button"{"" if _pi_counts[p] else " disabled title=" + chr(34) + "No award listed yet" + chr(34)}>{esc(p.split()[-1])} ({_pi_counts[p]})</button>' for p in _pis)
        + '</div></div><div class="frow"><span class="flab">Thrust</span>'
        '<button class="chip" data-f="thrust" data-v="all" aria-pressed="true" type="button">All</button>'
        + '<div class="fchips">' + "".join(f'<button class="chip" data-f="thrust" data-v="{esc(k)}" aria-pressed="false" type="button">{esc(t.split(" and ")[0].split(",")[0])}</button>' for k, t in _thrusts)
        + '</div></div><div class="frow"><span class="flab">Year</span>'
        '<button class="chip" data-f="year" data-v="all" aria-pressed="true" type="button">All</button>'
        + '<div class="fchips">' + "".join(f'<button class="chip" data-f="year" data-v="{y}" aria-pressed="false" type="button">{y}</button>' for y in _yrs if 2019 <= y <= datetime.date.today().year)
        + '</div></div></div><p class="pcount" id="pcount" aria-live="polite"></p>')
    projects_html = ""
    for pr in PROJECTS:
        tagcls = "tag new" if pr["tag"].startswith("New") else "tag"
        share = f'<small>{esc(pr["share"])}</small>' if pr.get("share") else ''
        amt = f'<div class="amt">{esc(pr["amount"])}{share}<small>{esc(pr["period"])}</small></div>' if pr["amount"] else f'<div class="amt"><small>{esc(pr["period"])}</small></div>'
        _pi = "|".join(n for n, _ in project_people(pr)); _yrs = " ".join(str(y) for y in project_years(pr))
        projects_html += (f'<div class="proj" data-pi="{esc(_pi)}" data-thrust="{esc(project_thrust(pr))}" data-years="{esc(_yrs)}" data-status="{esc(pr["tag"])}"><div class="when"><span class="{tagcls}">{esc(pr["tag"])}</span><br>{esc(pr["domain"])}</div>'
                          f'<div><h3>{esc(pr["title"])}</h3><div class="sponsor">{("<span class=" + chr(34) + "role" + chr(34) + ">" + esc(pr["role"]) + "</span>") if pr.get("role") else ""}{esc(pr["sponsor"])}</div>'
                          f'<p class="desc">{esc(pr["desc"])}</p><p class="team">{esc(pr["team"])}</p>'
                          + (f'<p class="projlink"><a href="{esc(pr["url"])}">{esc(pr.get("link", "Project page"))}</a></p>' if pr.get("url") else "")
                          + f'</div>{amt}</div>')

    def tool_fig(t):
        if TOOL_ART.get(t.get("art")):
            return f'<div class="toolfig">{TOOL_ART[t["art"]]}</div>'
        return ""
    tools_html = "".join(
        f'<div class="tool">{tool_fig(t)}<h4>{esc(t["name"])}</h4><p>{esc(t["what"])}</p>'
        f'{("<p class=" + chr(34) + "toollink" + chr(34) + "><a href=" + chr(34) + esc(t["url"]) + chr(34) + ">" + esc(t["link"]) + "</a></p>") if t.get("url") else ""}</div>'
        for t in TOOLS)

    d = FACULTY["director"]
    director_html = ('<div class="director">' + avatar(d, "xl") + '<div>' + person_card(d, with_photo=False) +
                     f'<div class="bio"><p>{esc(d["bio"])}</p></div></div></div>')
    core_html = '<div class="core">' + "".join(person_card(p, "lg") for p in FACULTY["core"]) + '</div>'
    aff_html = '<ul class="plist">' + "".join(person_row(p) for p in FACULTY["affiliated"]) + '</ul>'
    ext_html = '<ul class="plist">' + "".join(person_row(p) for p in FACULTY["external"]) + '</ul>'
    # Students grouped by primary advisor: the director's group first with full cards, then the other
    # center faculty in surname order, listed compactly until they send photos and research summaries.
    _adv_order = ["Vinod M. Vokkarane"] + sorted({s["advisor"] for s in STUDENTS} - {"Vinod M. Vokkarane"}, key=lambda n: n.split()[-1])
    _groups = []
    for adv in _adv_order:
        grp = [s for s in STUDENTS if s["advisor"] == adv]
        lab = " (Advanced Communication Networks Laboratory)" if adv == "Vinod M. Vokkarane" else ""
        head = f'<h3 class="advh">Advised by {esc(adv)}{lab} <span class="advn">{len(grp)}</span></h3>'
        if adv == "Vinod M. Vokkarane":
            body = '<div class="stugrid">' + "".join(student_card(st) for st in grp) + '</div>'
        else:
            body = '<ul class="stulist">' + "".join(
                f'<li><b>{esc(s["name"])}</b><span>{esc(s["status"])}</span><span class="prog">{esc(s.get("program", ""))}</span></li>' for s in grp) + '</ul>'
        _groups.append(f'<div class="advgroup">{head}{body}</div>')
    students_html = "".join(_groups)
    lablife_html = "".join(f'<img src="data:image/jpeg;base64,{IMG[f"lab{i}"]}" alt="Members of the Advanced Communication Networks Laboratory" width="760" height="406">' for i in range(1, 7) if IMG.get(f"lab{i}"))
    alumni_feat_html = "".join(alum_feature(a) for a in ALUMNI_FEATURED)
    alumni_phd_html = "".join(f'<li><span class="yr">{esc(y)}</span><span><b>{esc(n)}</b>{(" <span class=\"where\">" + esc(w) + "</span>") if w else ""}</span></li>' for y, n, w in ALUMNI_PHD)
    alumni_pd_html = "".join(f'<li><span><b>{esc(n)}</b>{(" <span class=\"where\">" + esc(w) + "</span>") if w else ""}</span></li>' for n, w in ALUMNI_POSTDOC)
    sponsors_html = "".join(
        f'<div class="sgroup"><h3>{esc(group)}</h3><div class="logos">' + "".join(logo_tile(sp) for sp in items) + '</div></div>'
        for group, items in SPONSORS.items())


    def render_pubs(items):
        out = ""
        cur = None
        for p in items:
            if p["year"] != cur:
                if cur is not None: out += "</ul>"
                cur = p["year"]; out += f'<div class="yearhead">{cur}</div><ul class="pubs">'
            kind = {"journal": '<span class="kind j">Journal</span>', "chapter": '<span class="kind c">Chapter</span>'}.get(p["type"], '<span class="kind">Conference</span>')
            link = f'https://doi.org/{p["doi"]}' if p["doi"] else None
            title = f'<a class="t" href="{esc(link)}">{esc(p["title"])}</a>' if link else f'<span class="t">{esc(p["title"])}</span>'
            side = kind + (f'<a href="{esc(link)}" title="doi:{esc(p["doi"])}">Publisher record</a>' if link else "")
            doi_line = f'<div class="doi">DOI <a href="{esc(link)}">{esc(p["doi"])}</a></div>' if link else ""
            chip = journal_chip(p["venue"]) if p["type"] == "journal" else ""
            out += (f'<li data-year="{p["year"]}" data-type="{p["type"]}" data-fac="{" ".join(p["faculty"])}">'
                    f'<div><div class="a">{fmt_authors(p["authors"])}</div>{title}'
                    f'<div class="v"><i>{esc(p["venue"])}</i>, {esc(p["details"])}{chip}</div>{doi_line}</div><div class="side">{side}</div></li>')
        if cur is not None: out += "</ul>"
        return out
    n_students = len(STUDENTS)
    n_alumni = len(ALUMNI_PROFILES)
    alumni_phd_cards, alumni_pd_cards = alumni_profiles_html()
    pubs_html = render_pubs(P)
    # Faculty filter chips come from CORE, so a faculty member added to the center gets a chip automatically:
    # the director first, then everyone else with papers in the record, by surname.
    _fac_with_papers = {f for p in P for f in p["faculty"]}
    fac_chips = "\n        ".join(f'<button class="chip" data-f="fac" data-v="{esc(f)}" aria-pressed="false">{esc(f)}</button>'
                                   for f in ["Vokkarane"] + sorted(CORE - {"Vokkarane"}) if f in _fac_with_papers)
    _recent = sorted(P, key=lambda p: (-p["year"], -(month_of(p) or 0), p["title"]))[:6]
    pub_teaser = render_pubs(_recent, grouped=False) if "grouped" in render_pubs.__code__.co_varnames else "".join(
        f'<li class="pub"><div><div class="a">{fmt_authors(p["authors"])}</div>'
        f'<div class="t">{("<a href=" + chr(34) + "https://doi.org/" + esc(p["doi"]) + chr(34) + ">" + esc(p["title"]) + "</a>") if p.get("doi") else esc(p["title"])}</div>'
        f'<div class="v"><i>{esc(p["venue"])}</i>, {esc(p["details"])}{journal_chip(p["venue"]) if p["type"] == "journal" else ""}</div></div></li>' for p in _recent)
    news_teaser = render_news(build_news_items(3) or build_news_items(12), limit=4)

    facts = [
        ("$2M", "NSF MRI Track 2 award for the SUMMIT federated smart grid testbed, 2026 to 2029"),
        (str(n_faculty), "affiliated faculty across engineering, computing, and medicine"),
        (str(n_pubs), f"papers from center faculty since 2019, {n_journal} in journals"),
        ("3", "application domains: energy and power, transportation, healthcare"),
    ]
    facts_html = "".join(f'<div><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in facts)

    hero_bg = f' style="background-image:url({img_src("hero")})"' if IMG.get("hero") else ""
    cyber_bg = f' style="background-image:url({img_src("cyber")})"' if IMG.get("cyber") else ""
    gallery_items = [
        ("about_aghara", "Prof. Sukesh Aghara talking with two students inside the UMass Lowell nuclear reactor", "Prof. Sukesh Aghara talks with students inside the UMass Lowell nuclear reactor."),
        ("about_luo", "Prof. Yan Luo with a student at a workstation in the lab", "Prof. Yan Luo with a student in the lab."),
        ("about_vokkarane", "Vinod Vokkarane talking with a colleague at the opening of the Raytheon-UMass Lowell Research Institute", "Vinod Vokkarane talks with a colleague at the opening of the Raytheon-UMass Lowell Research Institute."),
    ]
    about_photo = '<div class="gallery">' + "".join(
        f'<figure><img src="{img_src(k)}" alt="{esc(alt)}"><figcaption>{esc(cap)}</figcaption></figure>'
        for k, alt, cap in gallery_items if IMG.get(k)) + '</div>'
    lab_img = f'<div class="photo"><img src="{img_src("lab_robot")}" alt="Two UMass Lowell electrical and computer engineering students assembling a robot in a lab" width="1200" height="696"></div>' if IMG.get("lab_robot") else ""

    footer_html = f"""<footer id="contact" class="uml-footer" role="contentinfo">
  <div class="wrap">
    <div class="cols">
      <div class="col">
        <div class="flogo"><img src="{img_src("logo_name")}" alt="SCyPS, Center for Smart Cyber-Physical Systems" width="594" height="453"></div>
        <a href="https://www.uml.edu/" title="UMass Lowell home">{UML_LOGO}</a>
        <address><strong>Center for Smart Cyber-Physical Systems (SCyPS)</strong><br>UMass Lowell<br>1 University Ave. Lowell, MA 01854<br>Email: <a href="mailto:Vinod_Vokkarane@uml.edu">Vinod_Vokkarane@uml.edu</a></address>
        {social_links("follow")}
      </div>
      <div class="col menu">
        <nav aria-label="Footer menu"><h2>Menu</h2>
          <ul><li><a href="#about">About</a></li><li><a href="#research">Research</a></li><li><a href="#projects">Projects</a></li><li><a href="labs.html">Labs</a></li><li><a href="#sponsors">Sponsors</a></li><li><a href="people.html">People</a></li><li><a href="students.html">Students</a></li><li><a href="positions.html">Join</a></li><li><a href="alumni.html">Alumni</a></li><li><a href="publications.html">Publications</a></li><li><a href="insights.html">Insights</a></li><li><a href="news.html">News</a></li><li><a href="{GIFT_URL}">Make a Gift</a></li></ul>
        </nav>
      </div>
      <div class="col dir">
        <h2>Director</h2>
        <p>Vinod M. Vokkarane<br>Ball Hall 409, North Campus<br><a href="mailto:vinod_vokkarane@uml.edu">vinod_vokkarane@uml.edu</a><br>978-934-3345</p>
      </div>
      <div class="col social">
        <ul>
          <li><a href="https://www.tiktok.com/@umass_lowell" title="Find us on TikTok"><svg class="ico" viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M448,209.91a210.06,210.06,0,0,1-122.77-39.25V349.38A162.55,162.55,0,1,1,185,188.31V278.2a74.62,74.62,0,1,0,52.23,71.18V0l88,0a121.18,121.18,0,0,0,1.86,22.17h0A122.18,122.18,0,0,0,381,102.39a121.43,121.43,0,0,0,67,20.14Z"/></svg><span class="label">Find us on TikTok</span></a></li>
          <li><a href="https://www.facebook.com/umlowell" title="Find us on Facebook"><svg class="ico" viewBox="0 0 512 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M512 256C512 114.6 397.4 0 256 0S0 114.6 0 256C0 376 82.7 476.8 194.2 504.5V334.2H141.4V256h52.8V222.3c0-87.1 39.4-127.5 125-127.5c16.2 0 44.2 3.2 55.7 6.4V172c-6-.6-16.5-1-29.6-1c-42 0-58.2 15.9-58.2 57.2V256h83.6l-14.4 78.2H287V510.1C413.8 494.8 512 386.9 512 256h0z"/></svg><span class="label">Find us on Facebook</span></a></li>
          <li><a href="https://twitter.com/umasslowell" title="Follow us on X"><svg class="ico" viewBox="0 0 512 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M389.2 48h70.6L305.6 224.2 487 464H345L233.7 318.6 106.5 464H35.8L200.7 275.5 26.8 48H172.4L272.9 180.9 389.2 48zM364.4 421.8h39.1L151.1 88h-42L364.4 421.8z"/></svg><span class="label">Follow us on X</span></a></li>
          <li><a href="https://www.youtube.com/user/umasslowell" title="Watch us on YouTube"><svg class="ico" viewBox="0 0 576 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M549.655 124.083c-6.281-23.65-24.787-42.276-48.284-48.597C458.781 64 288 64 288 64S117.22 64 74.629 75.486c-23.497 6.322-42.003 24.947-48.284 48.597-11.412 42.867-11.412 132.305-11.412 132.305s0 89.438 11.412 132.305c6.281 23.65 24.787 41.5 48.284 47.821C117.22 448 288 448 288 448s170.78 0 213.371-11.486c23.497-6.321 42.003-24.171 48.284-47.821 11.412-42.867 11.412-132.305 11.412-132.305s0-89.438-11.412-132.305zm-317.51 213.508V175.185l142.739 81.205-142.739 81.201z"/></svg><span class="label">Watch us on YouTube</span></a></li>
          <li><a href="https://instagram.com/umasslowell" title="Find us on Instagram"><svg class="ico" viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/></svg><span class="label">Find us on Instagram</span></a></li>
          <li><a href="https://www.linkedin.com/school/university-of-massachusetts-lowell/" title="Find us on LinkedIn"><svg class="ico" viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"/></svg><span class="label">Find us on LinkedIn</span></a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="bottom">
    <div class="wrap">
      <ul>
        <li><a href="https://www.uml.edu/maps/" title="Interactive Campus Map and Directions">Maps &amp; Directions</a></li>
        <li><a href="https://www.uml.edu/directory/question.aspx" title="Contact Us at UMass Lowell">Contact Us</a></li>
        <li><a href="https://www.massachusetts.edu/" title="UMass System">UMass System</a></li>
        <li><a href="https://www.uml.edu/privacy-policy.aspx" title="Privacy Policy and Terms of Use">Privacy Policy</a></li>
        <li><a href="https://www.uml.edu/accessibility/" title="Accessibility and Accommodations">Accessibility</a></li>
        <li><a href="https://www.uml.edu/service/Apps/Forms/Form?configId=ccde10d9-949a-4891-a810-ca2cfa641f6f&amp;tfa_26=https://www.uml.edu/research/scyps/" title="Website Feedback">Feedback</a></li>
      </ul>
      <p class="fine">Updated {datetime.date.today().strftime("%B %Y")}. Grant figures are total awards as reported by sponsors; the UMass Lowell share is noted where a project is a multi-institution consortium. Photographs courtesy of UMass Lowell.</p>
      <p class="version">v {SITE_VERSION}<span class="vsep"></span><span id="visits" title="Visits counted since the counter went live"></span></p>
    </div>
  </div>
</footer>"""
    script_html = f"""<script>
(function(){{
  var root=document.documentElement, tb=document.getElementById('theme');
  function effective(){{ var t=root.getAttribute('data-theme'); if(t) return t; return (window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light'; }}
  function paintToggle(){{ var d=effective()==='dark'; tb.setAttribute('aria-label', d?'Switch to light mode':'Switch to dark mode'); tb.querySelector('.lbl').textContent=d?'Light':'Dark'; }}
  tb.addEventListener('click',function(){{ var next=effective()==='dark'?'light':'dark'; root.setAttribute('data-theme',next); try{{localStorage.setItem('scyps-theme',next);}}catch(e){{}} paintToggle(); }});
  paintToggle();
  // visitor counter (hits.sh): the one request this site makes to another party. It is made once per
  // visitor session, not on every page, and the badge hides if it cannot load or on file://.
  (function(){{
    var el=document.getElementById('visits'); if(!el) return;
    if(!/^https?:$/.test(location.protocol)){{ el.style.display='none'; return; }}
    var base=location.host+'/';   // one counter for the whole site
    var url='https://hits.sh/'+base+'.svg?view=total&style=flat-square&label=visits&color=0A777F&labelColor=0E2036';
    var counted=false; try{{ counted=sessionStorage.getItem('scyps-counted')==='1'; }}catch(e){{}}
    var img=new Image(); img.alt='visitors'; img.height=20;
    img.onerror=function(){{ el.style.display='none'; }};
    // the counting request happens once per session; later pages fetch the badge with view-only
    img.src = counted ? url.replace('view=total','view=total&count=false') : url;
    try{{ sessionStorage.setItem('scyps-counted','1'); }}catch(e){{}}
    el.textContent=''; el.appendChild(img);
  }})();
  // project filters: lead, thrust, and year, combined
  (function(){{
    var wrap=document.querySelector('.pfilters'); if(!wrap) return;
    var rows=[].slice.call(document.querySelectorAll('#projlist .proj')),
        out=document.getElementById('pcount'), state={{pi:'all',thrust:'all',year:'all'}};
    function apply(){{
      var n=0;
      rows.forEach(function(r){{
        var ok=(state.pi==='all'||(r.getAttribute('data-pi')||'').split('|').indexOf(state.pi)>-1)
             &&(state.thrust==='all'||r.getAttribute('data-thrust')===state.thrust)
             &&(state.year==='all'||(r.getAttribute('data-years')||'').split(' ').indexOf(state.year)>-1);
        r.hidden=!ok; if(ok) n++;
      }});
      if(out) out.textContent = (n===rows.length ? 'Showing all '+n+' projects' : 'Showing '+n+' of '+rows.length+' projects');
    }}
    wrap.querySelectorAll('.chip').forEach(function(c){{
      c.addEventListener('click', function(){{
        var f=c.getAttribute('data-f'); state[f]=c.getAttribute('data-v');
        wrap.querySelectorAll('.chip[data-f="'+f+'"]').forEach(function(o){{ o.setAttribute('aria-pressed', String(o===c)); }});
        apply();
      }});
    }});
    apply();
  }})();
  // news filters
  (function(){{
    var wrap=document.querySelector('.nfilters'); if(!wrap) return;
    var chips=[].slice.call(wrap.querySelectorAll('.chip')),
        items=[].slice.call(document.querySelectorAll('#newslist .nitem')),
        out=document.getElementById('ncount');
    function show(k){{
      var n=0;
      items.forEach(function(li){{
        var ok=(k==='all'||li.getAttribute('data-kind')===k);
        li.hidden=!ok; if(ok) n++;
      }});
      chips.forEach(function(c){{ c.setAttribute('aria-pressed', String(c.getAttribute('data-k')===k)); }});
      if(out) out.textContent = (k==='all' ? 'Showing all '+n+' items' : 'Showing '+n+' of '+items.length+' items');
    }}
    chips.forEach(function(c){{ if(!c.disabled) c.addEventListener('click', function(){{ show(c.getAttribute('data-k')); }}); }});
  }})();
  // pause SVG animations while their drawing is off screen
  if('IntersectionObserver' in window){{
    var io=new IntersectionObserver(function(es){{es.forEach(function(e){{e.target.classList.toggle('offscreen',!e.isIntersecting);}});}},{{rootMargin:'120px'}});
    document.querySelectorAll('svg').forEach(function(sv){{ if(sv.querySelector('.flow,.pulse,.spin,.grow,.trace,.fed-flow')) io.observe(sv); }});
  }}
  var tg=document.querySelector('.navtoggle'),menu=document.getElementById('menu');
  tg.addEventListener('click',function(){{var o=menu.classList.toggle('open');tg.setAttribute('aria-expanded',o);}});
  menu.addEventListener('click',function(e){{if(e.target.tagName==='A'){{menu.classList.remove('open');tg.setAttribute('aria-expanded','false');}}}});

  var links=[].slice.call(document.querySelectorAll('.links a'));
  var secs=links.filter(function(a){{return /^#/.test(a.getAttribute('href'));}}).map(function(a){{return document.querySelector(a.getAttribute('href'));}}).filter(Boolean);
  if('IntersectionObserver' in window){{
    var io=new IntersectionObserver(function(es){{
      es.forEach(function(en){{ if(en.isIntersecting){{ links.forEach(function(a){{a.setAttribute('aria-current',a.getAttribute('href')==='#'+en.target.id);}}); }} }});
    }},{{rootMargin:'-40% 0px -55% 0px'}});
    secs.forEach(function(s){{io.observe(s);}});
  }}

  var state={{fac:'all',type:'all',year:'all',q:''}};
  var items=[].slice.call(document.querySelectorAll('#publist .pubs li'));
  var total=items.length, count=document.getElementById('count');
  function apply(){{
    var q=state.q.trim().toLowerCase(), shown=0;
    items.forEach(function(li){{
      var ok=(state.fac==='all'||li.getAttribute('data-fac').split(' ').indexOf(state.fac)>-1)
          &&(state.type==='all'||li.getAttribute('data-type')===state.type)
          &&(state.year==='all'||li.getAttribute('data-year')===state.year)
          &&(!q||li.textContent.toLowerCase().indexOf(q)>-1);
      li.style.display=ok?'':'none'; if(ok)shown++;
    }});
    document.querySelectorAll('#publist .yearhead').forEach(function(h){{
      var ul=h.nextElementSibling, any=[].some.call(ul.children,function(li){{return li.style.display!=='none';}});
      h.style.display=any?'':'none'; ul.style.display=any?'':'none';
    }});
    if(count) count.textContent='Showing '+shown+' of '+total+' papers'+(shown?'':'. Nothing matches these filters; clear one to see more.');
  }}
  document.querySelectorAll('.chip').forEach(function(b){{
    b.addEventListener('click',function(){{
      var f=b.getAttribute('data-f');
      document.querySelectorAll('.chip[data-f="'+f+'"]').forEach(function(x){{x.setAttribute('aria-pressed','false');}});
      b.setAttribute('aria-pressed','true'); state[f]=b.getAttribute('data-v'); apply();
    }});
  }});
  var qEl=document.getElementById('q'); if(qEl) qEl.addEventListener('input',function(e){{state.q=e.target.value;apply();}});

  // (citation figures are printed at build time; no runtime lookups)
}})();
</script>"""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Center for Smart Cyber-Physical Systems (SCyPS) | UMass Lowell</title>
<meta name="description" content="UMass Lowell's Center for Smart Cyber-Physical Systems researches secure, resilient, and intelligent systems for energy, transportation, and healthcare: smart grid cybersecurity, optical and 6G networks, fault-tolerant edge computing, hardware security, and AI for cyber-physical control.">
<meta property="og:title" content="Center for Smart Cyber-Physical Systems (SCyPS) | UMass Lowell">
<meta property="og:description" content="Research, people, funded projects, and publications from UMass Lowell's Center for Smart Cyber-Physical Systems.">
<meta property="og:image" content="{SITE_URL}og-card.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}">
<link rel="alternate" type="application/rss+xml" title="SCyPS news" href="{SITE_URL}feed.xml">
{_ld(ld_organization())}
{_ld(ld_people())}
{_ld(ld_jobs())}
<meta property="og:type" content="website">
<link rel="icon" type="image/png" href="{img_src("favicon")}">
<link rel="preload" href="{FONT_ROOT}fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{FONT_ROOT}fonts/fraunces-latin-full-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{{font-family:"Fraunces";font-style:normal;font-weight:100 900;font-display:swap;src:url("{FONT_ROOT}fonts/fraunces-latin-full-normal.woff2") format("woff2")}}
@font-face{{font-family:"Fraunces";font-style:italic;font-weight:100 900;font-display:swap;src:url("{FONT_ROOT}fonts/fraunces-latin-full-italic.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-400-normal.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:italic;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-400-italic.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:500;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-500-normal.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:600;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-600-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-400-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:600;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-600-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:700;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-700-normal.woff2") format("woff2")}}
</style>

<style>{CSS}</style>
<script>(function(){{try{{var t=localStorage.getItem('scyps-theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="#top" aria-label="SCyPS home"><span class="mark"><img src="{img_src("logo_mark")}" alt="" width="576" height="271"></span><span>SCyPS<small>Center for Smart Cyber-Physical Systems, UMass Lowell</small></span></a>
    <div class="navright">
    <ul class="links" id="menu">
      <li><a href="#about">About</a></li>
      <li><a href="#research">Research</a></li>
      <li><a href="#projects">Projects</a></li>
      <li><a href="labs.html">Labs</a></li>
      <li><a href="#sponsors">Sponsors</a></li>
      <li><a href="people.html">People</a></li>
      <li><a href="students.html">Students</a></li>
      <li><a href="alumni.html">Alumni</a></li>
      <li><a href="publications.html">Publications</a></li>
      <li><a href="insights.html">Insights</a></li>
      <li><a href="news.html">News</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <a class="gift" href="{GIFT_URL}">Make a Gift</a>
    <button class="theme" id="theme" type="button" aria-label="Switch to dark mode"><svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></svg><span class="lbl">Dark</span></button>
    <button class="navtoggle" aria-expanded="false" aria-controls="menu">Menu</button>
    </div>
  </div>
</header>

<main id="main">
<div class="hero" id="top">
  <div class="bg" role="img" aria-label="City skyline overlaid with a wireless communication network"{hero_bg}></div>
  <div class="veil"></div>
  <div class="wrap hero-grid">
    <div>
    <h1>Where computation meets the physical world.</h1>
    <p class="lede">Power grids, roads, and hospitals now run on networks, sensors, and software. The Center for Smart Cyber-Physical Systems brings UMass Lowell researchers in networking, security, distributed computing, hardware, and AI together with domain experts to keep that infrastructure secure, resilient, and working under attack, failure, and disaster.</p>
    <div class="cta"><a class="btn primary" href="#research">Explore our research</a><a class="btn" href="#publications">Recent publications</a></div>
    </div>
    <div class="hero-logo"><img src="{img_src("logo_full")}" alt="SCyPS: Center for Smart Cyber-Physical Systems. People, systems, a safer tomorrow." width="598" height="508"></div>
  </div>
</div>

<div class="factsbar"><div class="wrap"><div class="facts">{facts_html}</div></div></div>

<section id="about">
  <div class="wrap">
    <div class="shead"><h2>A center built around the systems a smart society runs on</h2>
      <p>Power grids, roads, and hospitals now depend on fast networks connected to instrumentation, control systems, and IoT devices. SCyPS develops practical, high-impact ways to make those heterogeneous distributed systems more reliable, scalable, secure, and private.</p></div>
    {about_photo}
    <div class="hubwrap">
      <figure class="hubfig">{HUB}</figure>
      <div class="hublist">
        <h3>The center serves as a hub for</h3>
        <ol>
          <li>research on secure, resilient, and efficient cyber-physical systems, in eight thrusts each with a named lead;</li>
          <li>shared testbeds and instruments, including SUMMIT, open to collaborators;</li>
          <li>training the cyber-physical systems workforce, from doctoral students to co-ops;</li>
          <li>partnership with industry, agencies, and the community on problems they actually have; and</li>
          <li>open-source tools and technology transfer that put results into practice.</li>
        </ol>
      </div>
    </div>
    <h2 class="grouph orgh">How the center is organized</h2>
    <figure class="orgfig">{ORG}</figure>
    <p class="orgnote">A director and an executive committee, advised by an external board and an industry council. Eight research thrusts, each with a named lead who is the point of contact for collaborators and sponsors in that area. Write to the director at <a href="mailto:Vinod_Vokkarane@uml.edu">Vinod_Vokkarane@uml.edu</a> or to the thrust lead directly.</p>

    <div class="about-grid">
      <div>
        <h3>Mission</h3>
        <p>The Center for Smart Cyber-Physical Systems (SCyPS) develops secure, resilient, and trustworthy cyber-physical systems for the infrastructure people depend on: the energy grid, transportation, health care, and advanced manufacturing. Its faculty in engineering, computing, science, philosophy, and education take an interdisciplinary approach to the reliability, scalability, resource use, security, and privacy of these systems, and to the trust between people and the automation they work with.</p>
        <p>The center carries UMass Lowell's mission into its field. The university exists to give students an excellent, affordable education, to meet the needs of the Commonwealth, and to advance sustainable technologies and communities through teaching, research, scholarship, and engagement. SCyPS does that by training the engineers and scientists who will build and defend critical infrastructure, by producing research the Commonwealth's utilities, agencies, and industries can use, and by working with industry, government, and community partners so that its results reach the people of Massachusetts and beyond.</p>
        <h3 style="margin-top:22px">Vision</h3>
        <p>The Center for Smart Cyber-Physical Systems (SCyPS) will establish itself as an internationally recognized center for research and education focused on innovation, evaluation, and optimization of hardware and software technologies for an advanced, smart society.</p>
        <div class="domains"><span>Energy and power</span><span>Transportation</span><span>Healthcare</span><span>Additive manufacturing</span></div>
      </div>
      <div>
        <h3>Goals</h3>
        <ul class="goals">
          <li><h4>Research</h4><p>The SCyPS Center will become the hub of research and innovation on smart cyber-physical systems addressing challenges in healthcare, transportation and energy. SCyPS brings together a unique multidisciplinary team of experts in networking, data security, high performance computing, advanced communications, robotics, digital health care, power and nuclear engineering, and smart and connected transportation to create an environment that fosters and encourages collaboration on research central to the safety, efficiency, performance, and innovation of smart cyber-physical systems.</p></li>
          <li><h4>Student Development and Training</h4><p>The SCyPS Center focuses on the education and development of students and postdoctoral researchers, providing hands-on training and an immersive environment to meet the demand for a skilled, innovative workforce of tomorrow. PhD graduates and postdocs from SCyPS will experience professional growth opportunities and will be prepared to secure prominent positions in academic institutions and research labs in major companies.</p></li>
          <li><h4>Industry and Community Engagement</h4><p>The SCyPS Center will work collaboratively with industry partners to share ideas and conduct high-impact research to meet the evolving needs of industry sectors. By cultivating a symbiotic relationship, industry members will have the opportunity to proactively contribute to the success and path of the center while gaining access to talented, skilled students as co-ops, interns and employees.</p></li>
        </ul>
      </div>
    </div>
    <div class="loop">
      <figure class="schem">{SCHEMATIC}</figure>
      <div class="txt">
        <h3>One loop, three domains</h3>
        <p>Every system the center studies closes the same loop: physical processes are sensed at the edge, carried over optical and wireless transport, analysed by AI and high-performance computing, and controlled in real time. The research question is how to keep that loop fast, trustworthy, and recoverable when parts of it are attacked or fail.</p>
      </div>
    </div>
  </div>
</section>

<section id="research" class="tint">
  <div class="wrap">
    <div class="shead"><h2>Research thrusts</h2><p>Eight connected lines of work, each with a named lead who is accountable for it. Most projects cut across two or three, which is the point of running them under one roof.</p></div>
    <div class="thrusts">{thrusts_html}</div>
  </div>
</section>

<section id="projects">
  <div class="wrap">
    <div class="shead"><h2>Funded projects</h2><p>Sponsored research led by center faculty, current awards first, then completed awards. Four new awards started in 2026, headed by the NSF MRI SUMMIT testbed.</p></div>
    <div class="feature">
      <div class="copy">
        <span class="kicker">New in 2026</span>
        <h3>SUMMIT: a three-site smart grid testbed you can attack, defend, and restore</h3>
        <p>NSF's Major Research Instrumentation program is funding a federated cyber-physical instrument that links real-time power system simulation, grid communication networks, and control and cybersecurity hardware across UMass Lowell, NYU, and West Virginia University. RTDS real-time digital simulators run high-fidelity models of the Northeast's backbone transmission grid fast enough to drive real controllers and network hardware in the loop, and a wide-area software-defined network ties the three sites together over the Internet. Researchers at any site will be able to run attack, defense, and restoration experiments on the shared testbed, and students will train on the same equipment utilities and vendors use.</p>
        <div class="meta">
          <div><b>$2.0M</b><span>NSF MRI Track 2, Award #2511635</span></div>
          <div><b>Oct 2026 to Sep 2029</b><span>award period</span></div>
          <div><b>Vinod Vokkarane, PI</b><span>Co-PIs Orlando Arias, Lewis Tseng, Yuzhang Lin, Anurag Srivastava; senior personnel Yan Luo, Seung Woo Son, Christopher Niezrecki</span></div>
          <div><b>Positions open</b><span><a href="{POSTDOC_URL}">Postdoctoral research associate</a> on SUMMIT, and fully funded <a href="positions.html">M.S. research assistantships</a> on BOND-AI and ARPO (U.S. citizens only)</span></div>
        </div>
      </div>
      <div class="paradigms">
        <h4>Four paradigms</h4>
        <ol>
          <li><b>Distributed hardware-in-the-loop (HIL) simulation.</b> Control, networking, and cybersecurity hardware closes the loop with real-time grid models running on RTDS simulators.</li>
          <li><b>Internet-in-the-loop simulation.</b> The three sites exchange live simulation signals over a wide-area software-defined network across the public Internet.</li>
          <li><b>Heterogeneous distributed digital twins.</b> Scoped in this phase to the RTDS simulators and the existing OPAL-RT simulator, relocated to UML North.</li>
          <li><b>Federated platform for HIL Simulation-as-a-Service.</b> The central objective: a federation limited in this phase to the three partner universities, with WVU's existing testbed as the first instrument federated. National-scale federation is planned for Phase 2.</li>
        </ol>
        <p class="scope">Phase 1 models the backbone transmission grid of the Northeast; distribution grids are future work. All power components, including generation, storage, and inverters, are modeled at high fidelity inside the RTDS simulators, so no power hardware is installed on site. Grid instances are small to medium scale for proof of concept while keeping every capability needed to scale to regional and national models. Physical asset monitoring and the electric vehicle course move to Phase 2.</p>
        <p class="more"><a class="btn-gift summit-btn" href="summit.html">Full SUMMIT project page</a></p>
      </div>
      <figure class="arch">
        <img src="{img_src("summit_arch")}" alt="SUMMIT architecture: at the UMass Lowell main site, signal generator, power amplifier, grid simulator, network emulator, and optical, RF, and FPGA equipment connect to an RTDS real-time digital simulator and a control and monitoring workstation through a core network switch; a wide-area network over the Internet links the WVU and NYU sites, each with its own switch, controller, and simulator" width="1800" height="748">
        <figcaption>SUMMIT architecture: the UMass Lowell main site, the wide-area software-defined network, and the WVU and NYU federation sites</figcaption>
      </figure>
    </div>
    {projfilters}
    <div class="ledger" id="projlist">{projects_html}</div>
    <div class="tools">{tools_html}</div>
  </div>
</section>

<section id="sponsors">
  <div class="wrap">
    <div class="shead"><h2>Sponsors and partners</h2><p>The agencies, companies, and institutions that have funded the center's research and that of its faculty.</p></div>
    {sponsors_html}
    <div class="ack">
      <p>This material is based upon work supported by the U.S. National Science Foundation under Grant No. 2511635. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.</p>
      <p>Research at the center is also supported by the U.S. Department of Energy, the Office of Naval Research, the U.S. Army, the Commonwealth of Massachusetts, the International Atomic Energy Agency, the Massachusetts Technology Collaborative, Red Hat, and Navia Energy.</p>
    </div>
  </div>
</section>

<section id="people" class="tint">
  <div class="wrap">
    <div class="shead"><h2>People</h2><p>{n_faculty} faculty from three colleges, doctoral students in the director's group, and the graduates who have gone on to faculty positions and industry research.</p></div>
    <div class="peoplecards">
      <a class="pcard" href="people.html"><span class="pnum">{n_faculty}</span><span class="plab">Faculty</span><span class="pdesc">The director, center faculty, affiliated researchers across engineering, sciences, and humanities, and external collaborators.</span><span class="pgo">All faculty</span></a>
      <a class="pcard" href="students.html"><span class="pnum">{n_students}</span><span class="plab">Doctoral students</span><span class="pdesc">Students in the Advanced Communication Networks Laboratory working on center projects, with their research focus.</span><span class="pgo">Meet the students</span></a>
      <a class="pcard" href="alumni.html"><span class="pnum">{n_alumni}</span><span class="plab">Ph.D. alumni</span><span class="pdesc">Where the group's graduates and postdoctoral researchers went, from faculty posts to Google, AT&amp;T, and KLA.</span><span class="pgo">Where they are now</span></a>
    </div>
  </div>
</section>

<section id="publications" class="tint">
  <div class="wrap">
    <div class="shead"><h2>Publications</h2><p>{n_pubs} peer-reviewed papers from the director and center faculty since 2019, {n_journal} of them in journals. The newest are below; the full list is searchable and filterable on its own page, and the <a href="insights.html">insights page</a> reads the whole record together: research clusters, who works with whom, what the work builds on, and reach.</p></div>
    <ol class="publist teaser">{pub_teaser}</ol>
    <p class="more"><a class="btn-gift summit-btn" href="publications.html">All {n_pubs} publications</a></p>
  </div>
</section>

<section id="news">
  <div class="wrap">
    <div class="shead"><h2>News</h2><p>What has happened in the last few months, generated from the center's own record of papers, awards, and milestones.</p></div>
    <ol class="timeline">{news_teaser}</ol>
    <p class="more"><a class="btn-gift summit-btn" href="news.html">All news and the latest papers</a></p>
  </div>
</section>

<section id="join">
  <div class="wrap">
    <div class="shead"><h2>Work with us</h2><p>The center is growing with the SUMMIT testbed, and there is room for students, postdocs, and partners.</p></div>
    <div class="join">
      {lab_img}
      <div>
        <div class="block">
          <h3>Students and postdocs</h3>
          <p>Ph.D. and M.S. students in the center work on real instruments and real data: the federated smart grid testbed, multi-band optical network simulation, fault-tolerant edge systems, and hardware security. A postdoctoral research associate position on SUMMIT is open in Fall 2026 (<a href="{POSTDOC_URL}">application</a>). Prospective students should write to a faculty member whose work matches their interests and copy the director, Vinod_Vokkarane@uml.edu.</p>
        </div>
        <div class="block">
          <h3>Industry and agency partners</h3>
          <ul>
            <li>Run attack, defense, and restoration experiments on the SUMMIT testbed once it opens to collaborators.</li>
            <li>Sponsor targeted research and gain early access to results and open-source tools such as <a href="{FUSION_URL}">FUSION</a>.</li>
            <li>Recruit co-ops, interns, and graduates trained on cyber-physical infrastructure.</li>
            <li>Join proposals to NSF, DOE, DoD, and state programs as a partner site or end user.</li>
          </ul>
        </div>
        <div class="block capbox">
          <h3>Sponsor a senior capstone team for $25K</h3>
          <p>For $25,000 a company or agency gets a team of four to six UMass Lowell seniors in computer, electrical, mechanical, or plastics engineering for their full senior year, working a problem you define under a faculty coach and your own project liaison. Each student puts in 10 to 12 hours a week for two semesters, and you receive a problem clarification report, a solution proposal, a project update, and a final report and presentation, with weekly progress memos in between.</p>
          <p>Through the center, the project comes with a cyber-physical focus: smart grid security, connected transportation, optical and 6G networks, edge computing, or hardware security, with access to the center's testbeds and faculty. Past sponsors of the college's capstone program include Raytheon, Analog Devices, BAE Systems, New Balance, and Entegris. The fee supports the students and the program; it is not a contract for deliverables, and arrangements for sensitive data or delayed publication are made before the project starts.</p>
          <p class="capcta"><a class="btn-gift" href="{GIFT_URL}">Sponsor a team</a> <a class="capmail" href="mailto:Vinod_Vokkarane@uml.edu?subject=Sponsoring%20a%20senior%20capstone%20team">Write to the director to scope a project</a></p>
          <p class="capfine">Sponsorship is arranged with the Francis College of Engineering; the director will introduce you to the capstone program office. Teams form in the spring for the following academic year, so a project proposed by April is staffed in September.</p>
        </div>
        <div class="block giftbox">
          <h3>Support the Center for Smart Cyber-Physical Systems</h3>
          <p>Contribute to research and workforce development that keeps power, transportation, and health infrastructure secure and resilient. Your gift to the center supports the SUMMIT testbed, student travel and summer research positions, and the students whose careers will run the systems a smart society depends on.</p>
          <a class="btn-gift" href="{GIFT_URL}">Donate to the Center</a>
        </div>
        {social_links("follow follow-light")}
      </div>
    </div>
  </div>
</section>
</main>

{footer_html}

{script_html}
</body>
</html>
"""
    page = new_tab_links(page)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    build_summit(footer_html, script_html)
    build_publications(PUBS_SECTION.replace("{fac_chips}", fac_chips).replace("{n_pubs}", str(n_pubs)).replace("{pubs_html}", pubs_html), footer_html, script_html)
    build_people_pages({
        "people": (PEOPLE_SECTION.replace("{director_html}", director_html).replace("{core_html}", core_html)
                   .replace("{aff_html}", aff_html).replace("{ext_html}", ext_html) + collab_graph_html()),
        "students": (STUDENTS_SECTION.replace("{students_html}", students_html).replace("{lablife_html}", lablife_html)
                     .replace("{spotlight_teaser}", spotlight_article(max(SPOTLIGHTS, key=lambda s: s["ym"]), full=False) if SPOTLIGHTS else "")),
        "alumni": (ALUMNI_SECTION.replace("{alumni_feat_html}", alumni_feat_html)
                   .replace("{alumni_phd_cards}", alumni_phd_cards).replace("{alumni_pd_cards}", alumni_pd_cards)),
    }, footer_html, script_html)
    build_newspage(footer_html, script_html)
    build_thrust_pages(footer_html, script_html)
    build_insights(footer_html, script_html)
    build_acnl(footer_html, script_html)
    build_labs(footer_html, script_html)
    build_spotlight(footer_html, script_html)
    build_positions(footer_html, script_html)
    try:
        import subprocess as _sp
        _r = _sp.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_acnl_site.py")], capture_output=True, text=True, timeout=300)
        print((_r.stdout or _r.stderr).strip().splitlines()[-1] if (_r.stdout or _r.stderr).strip() else "acnl/: built")
    except Exception as _e:
        print(f"acnl/ site skipped: {_e}")
    build_meta_files()
    build_feed()
    build_assets()
    _nl = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--newsletter=")), None)
    build_print_viewers(footer_html, script_html)
    if _nl: build_newsletter(_nl, footer_html, script_html)
    else: build_newsletter_index(footer_html, script_html)
    print(f"wrote {OUT} (v{SITE_VERSION}): {len(page)/1024:.0f} KB; {n_pubs} pubs ({n_journal} journal); {n_faculty} faculty; {len(IMG)} images embedded")


def new_tab_links(page):
    """Add target=_blank and rel=noopener to every http(s) link that lacks a target."""
    def fix(m):
        tag = m.group(0)
        if 'target=' in tag: return tag
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'
    return re.sub(r'<a\s[^>]*href="https?://[^"]*"[^>]*>', fix, page)


PUBS_SECTION = '<section id="publications">\n  <div class="wrap">\n    <div class="shead"><h2>Publications</h2><p>Peer-reviewed journal papers, conference papers, and book chapters from the director and center faculty since the center was founded in 2019, with links to the publisher\'s record. Center authors are shown in bold. Affiliated researchers and external collaborators publish widely in their own fields; their records are linked from their profiles.</p></div>\n    <div class="filters" role="group" aria-label="Filter publications">\n      <div class="fgroup"><span class="lab">Faculty</span>\n        <button class="chip" data-f="fac" data-v="all" aria-pressed="true">All</button>\n        {fac_chips}\n\n\n\n\n\n\n\n      </div>\n      <div class="fgroup"><span class="lab">Year</span>\n        <button class="chip" data-f="year" data-v="all" aria-pressed="true">All</button>\n        <button class="chip" data-f="year" data-v="2026" aria-pressed="false">2026</button>\n        <button class="chip" data-f="year" data-v="2025" aria-pressed="false">2025</button>\n        <button class="chip" data-f="year" data-v="2024" aria-pressed="false">2024</button>\n        <button class="chip" data-f="year" data-v="2023" aria-pressed="false">2023</button>\n        <button class="chip" data-f="year" data-v="2022" aria-pressed="false">2022</button>\n        <button class="chip" data-f="year" data-v="2021" aria-pressed="false">2021</button>\n        <button class="chip" data-f="year" data-v="2020" aria-pressed="false">2020</button>\n        <button class="chip" data-f="year" data-v="2019" aria-pressed="false">2019</button>\n      </div>\n      <div class="fgroup"><span class="lab">Type</span>\n        <button class="chip" data-f="type" data-v="all" aria-pressed="true">All</button>\n        <button class="chip" data-f="type" data-v="journal" aria-pressed="false">Journal</button>\n        <button class="chip" data-f="type" data-v="conference" aria-pressed="false">Conference</button>\n        <button class="chip" data-f="type" data-v="chapter" aria-pressed="false">Chapter</button>\n      </div>\n      <div class="search"><label for="q" class="lab">Search</label><input id="q" type="search" placeholder="title, author, or venue" autocomplete="off"></div>\n    </div>\n    <div class="count" id="count" aria-live="polite">Showing {n_pubs} of {n_pubs} papers</div>\n    <div id="publist">{pubs_html}</div>\n    <p class="pubnote">Records verified against Crossref (the NSDI paper is listed from the USENIX program). Journal chips show the Journal Impact Factor from Clarivate\'s Journal Citation Reports for the year given, and the SCImago quartile where available. Venues that do not register DOIs, such as ANS Transactions and INMM proceedings, are not captured, and for faculty with common names only papers with a confirmed UMass Lowell affiliation are included. A paper counts for a member only from the year they joined UMass Lowell; Yuzhang Lin\'s papers count when co-authored with another center faculty member. Send corrections or additions to Vinod_Vokkarane@uml.edu.</p>\n  </div>\n</section>'

FULL_NAME = {}
for _g in ("director", "core", "affiliated", "external"):
    for _p in ([FACULTY[_g]] if _g == "director" else FACULTY[_g]):
        _sur = re.sub(r"\(.*?\)", "", _p["name"]).split()[-1]
        FULL_NAME[_sur] = _p["name"]

PEOPLE_SECTION = '<section id="people" class="tint">\n  <div class="wrap">\n    <div class="shead"><h2>People</h2><p>Faculty from the Francis College of Engineering, the Kennedy College of Sciences, and the College of Fine Arts, Humanities and Social Sciences, plus long-running collaborators at partner universities and companies. Each profile links to the person\'s Google Scholar and ORCID records; citation totals are quoted from Google Scholar where the profile is public.</p></div>\n    <p class="founding">The center was founded on October 1, 2019 by Vinod Vokkarane, Martin Margala, Yan Luo, Sukesh Aghara, and Yuanchang Xie. Vokkarane served on the founding Board of Directors from October 2019 to July 2021 and has been director since August 2021. Margala, then Professor and Chair of Electrical and Computer Engineering, was founding co-director until July 2021 and remains an external collaborator.</p>\n    <h2 class="grouph">Center faculty</h2>\n    {director_html}\n    {core_html}\n    <div class="group"><h2 class="grouph">Affiliated researchers</h2><p>UMass Lowell faculty who collaborate on center projects and proposals.</p>{aff_html}</div>\n    <div class="group"><h2 class="grouph">External collaborators</h2><p>Partners at other universities and companies who work with the center on current projects.</p>{ext_html}</div>\n  </div>\n</section>\n\n'

STUDENTS_SECTION = '<section id="students">\n  <div class="wrap">\n    <div class="shead"><h2>Students</h2><p>Doctoral students of the center faculty, grouped by primary advisor. The director\'s group is the Advanced Communication Networks Laboratory.</p></div>\n    {spotlight_teaser}\n    <h2 class="grouph">Doctoral students</h2>\n    {students_html}\n    <div class="lablife">\n      <h3>Lab life</h3>\n      <p>The Advanced Communication Networks Laboratory through the years.</p>\n      <div class="labgrid">{lablife_html}</div>\n    </div>\n  </div>\n</section>\n\n'

ALUMNI_SECTION = '<section id="alumni" class="tint">\n  <div class="wrap">\n    <div class="shead"><h2>Alumni</h2><p>Where the group\'s Ph.D. graduates and postdoctoral researchers have gone.</p></div>\n    <h2 class="grouph">Recent graduates</h2>\n    <div class="stugrid two">{alumni_feat_html}</div>\n    <h2 class="grouph">Ph.D. graduates</h2>\n    <p class="alnote">Where each graduate is now, verified in September 2026 against employer pages, LinkedIn, and Google Scholar. Citation figures refresh monthly with the rest of the site.</p>\n    <div class="alumgrid">{alumni_phd_cards}</div>\n    <h2 class="grouph">Postdoctoral alumni</h2>\n    <div class="alumgrid">{alumni_pd_cards}</div>\n  </div>\n</section>\n\n'

# ---------------------------------------------------------------- news generation
def _pub_ym(p):
    return (p["year"], month_of(p) or 12)

def _period_start(period):
    """'Oct 2026 to Sep 2029' or '2026 to 2027' -> (year, month)."""
    m = re.match(r"([A-Z][a-z]{2})[a-z]*\.?\s+(\d{4})", period or "")
    if m:
        mon = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}.get(m.group(1), 1)
        return (int(m.group(2)), mon)
    m = re.match(r"(\d{4})", period or "")
    return (int(m.group(1)), 1) if m else None

def _months_ago(ym, n, ahead=4):
    """Inside the window: not older than n months, not dated more than `ahead` months in the future."""
    total = ym[0] * 12 + ym[1]
    now = datetime.date.today()
    cur = now.year * 12 + now.month
    return cur - n < total <= cur + ahead

def _is_future(ym):
    now = datetime.date.today()
    return ym[0] * 12 + ym[1] > now.year * 12 + now.month

def build_news_items(window_months=3):
    """Everything the site knows that happened recently, newest first."""
    items = []
    # papers, grouped by venue so a three-paper month does not read as three identical lines
    recent = [p for p in P if _months_ago(_pub_ym(p), window_months)]
    by_venue = {}
    for p in sorted(recent, key=lambda p: (-_pub_ym(p)[0], -_pub_ym(p)[1])):
        by_venue.setdefault((p["venue"], _pub_ym(p)), []).append(p)
    for (venue, ym), group in by_venue.items():
        names = sorted({FULL_NAME.get(f, f) for p in group for f in p["faculty"]})
        who = ", ".join(names[:3]) + (" and others" if len(names) > 3 else "")
        if len(group) == 1:
            title = group[0]["title"]
            body = f"{who} published in {venue}."
        else:
            title = f"{len(group)} papers in {venue}"
            body = f"{who} published {len(group)} papers in {venue}: " + "; ".join(g["title"] for g in group[:3]) + ("." if len(group) <= 3 else ", and more.")
        link = ("https://doi.org/" + group[0]["doi"]) if group[0].get("doi") else None
        kinds = {p["type"] for p in group}
        if kinds == {"journal"}: kind, cls, key = "Journal", "journal", "journal"
        elif kinds == {"conference"}: kind, cls, key = "Conference", "conf", "conference"
        elif kinds == {"chapter"}: kind, cls, key = "Chapter", "chapter", "chapter"
        else: kind, cls, key = "Papers", "", "journal"
        post = (f'{who}: "{group[0]["title"]}" in {venue}.' if len(group) == 1
                else f'{who}: {len(group)} new papers in {venue}.')
        items.append(dict(ym=ym, kind=kind, cls=cls, key=key, title=title, body=body,
                          link=link, linktext="Publisher record" if link else "", post=post))
    # awards that started inside the window
    for pr in PROJECTS:
        ym = _period_start(pr.get("period", ""))
        if not ym or not _months_ago(ym, window_months): continue
        amt = f' ({pr["amount"]})' if pr.get("amount") else ""
        items.append(dict(ym=ym, kind="Award", cls="award", key="award", title=pr["title"],
                          body=f'{pr["sponsor"]}{amt}. {pr["desc"]}', link=None, linktext="",
                          post=f'New award: {pr["title"]}. {re.sub(r" *\(Award #\d+\)", "", pr["sponsor"])}{amt}.'))
    # curated milestones from NEWS
    for when, text in NEWS:
        m = re.match(r"([A-Za-z]{3})[a-z]*\s+(\d{4})", when)
        if not m: continue
        mon = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}.get(m.group(1))
        ym = (int(m.group(2)), mon or 1)
        if not _months_ago(ym, window_months): continue
        parts = re.split(r"(?<=[a-z0-9\)])\.\s+(?=[A-Z])", text, maxsplit=1)
        head = parts[0].rstrip(".")
        if any(head[:40] in it["title"] or it["title"][:40] in head for it in items): continue
        talk = re.search(r"\b(present(s|ed|ation)|invited talk|keynote|panel|workshop|demo|poster|General Chair|chairs?)\b", text, re.I)
        kind, cls, key = ("Presentation", "talk", "presentation") if talk else ("Milestone", "milestone", "milestone")
        tail = parts[1].strip() if len(parts) > 1 else ""
        items.append(dict(ym=ym, kind=kind, cls=cls, key=key, title=head,
                          body=tail, link=None, linktext="", post=text))
    # an award row and a hand-written note about the same award would post twice; keep one
    seen = []
    for it in sorted(items, key=lambda i: (0 if i["key"] == "milestone" else 1)):
        key_words = set(re.findall(r"[A-Za-z]{4,}", it["title"].lower())[:6])
        if any(len(key_words & s2) >= 3 for s2 in seen): it["dup"] = True
        else: seen.append(key_words)
    items = [i for i in items if not i.get("dup")]
    items.sort(key=lambda i: (-i["ym"][0], -i["ym"][1]))
    return items

def render_news(items, limit=None):
    out = []
    for it in (items[:limit] if limit else items):
        future = _is_future(it["ym"])
        suffix = " issue" if (future and it.get("key") in ("journal", "chapter")) else (" start" if (future and it.get("key") == "award") else "")
        when = f'{MONTH_NAME[it["ym"][1]]} {it["ym"][0]}' + suffix
        link = f'<p class="nlink"><a href="{esc(it["link"])}">{esc(it["linktext"])}</a></p>' if it.get("link") else ""
        out.append(f'<li class="nitem" data-kind="{esc(it.get("key", "milestone"))}"><div class="nwhen">{esc(when)}</div><div>'
                   f'<span class="nkind {it["cls"]}">{esc(it["kind"])}</span>'
                   f'<h3>{esc(it["title"])}</h3><p>{esc(it["body"])}</p>{link}</div></li>')
    return "".join(out)

MONTH_NAME = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def stream_html(n=24):
    """The right-hand column: the newest papers, newest first."""
    rows = sorted(P, key=lambda p: (-p["year"], -(month_of(p) or 0), p["title"]))[:n]
    out = []
    for p in rows:
        t = esc(p["title"])
        t = f'<a href="https://doi.org/{esc(p["doi"])}">{t}</a>' if p.get("doi") else t
        out.append(f'<li><span class="k">{esc(p["type"])}</span><span class="t">{t}</span>'
                   f'<span class="v">{esc(p["venue"])}, {esc(p["details"])}</span></li>')
    return "".join(out)

# ---------------------------------------------------------------- shared page shell
def page_shell(title, desc, body, footer_html, script_html, extra_css="", active="", h1=None, canonical="", ld=""):
    nav = " ".join(
        f'<li><a href="{href}"{" class=\"on\"" if key == active else ""}>{label}</a></li>'
        for key, label, href in [
            ("about", "About", "index.html#about"), ("research", "Research", "index.html#research"),
            ("projects", "Projects", "index.html#projects"), ("labs", "Labs", "labs.html"),
            ("sponsors", "Sponsors", "index.html#sponsors"),
            ("people", "People", "people.html"), ("students", "Students", "students.html"), ("positions", "Join", "positions.html"),
            ("alumni", "Alumni", "alumni.html"), ("publications", "Publications", "publications.html"),
            ("insights", "Insights", "insights.html"), ("news", "News", "news.html"), ("contact", "Contact", "index.html#contact")])
    foot = footer_html.replace('href="#', 'href="index.html#')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE_URL}{esc(canonical) if canonical.endswith(".png") else "og-card.png"}">
<meta name="twitter:card" content="summary_large_image">
{f'<link rel="canonical" href="{SITE_URL}{esc(canonical)}">' if canonical else ""}
<link rel="alternate" type="application/rss+xml" title="SCyPS news" href="{SITE_URL}feed.xml">
{ld}
<link rel="preload" href="{FONT_ROOT}fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{FONT_ROOT}fonts/fraunces-latin-full-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{{font-family:"Fraunces";font-style:normal;font-weight:100 900;font-display:swap;src:url("{FONT_ROOT}fonts/fraunces-latin-full-normal.woff2") format("woff2")}}
@font-face{{font-family:"Fraunces";font-style:italic;font-weight:100 900;font-display:swap;src:url("{FONT_ROOT}fonts/fraunces-latin-full-italic.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-400-normal.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:italic;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-400-italic.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:500;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-500-normal.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:600;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-600-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-400-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:600;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-600-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:700;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-700-normal.woff2") format("woff2")}}
</style>

<link rel="icon" type="image/png" href="{img_src("favicon")}">
<style>{CSS}
.links a.on{{color:var(--ink);font-weight:600}}
{extra_css}</style>
<script>(function(){{try{{var t=localStorage.getItem('scyps-theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="SCyPS home"><span class="mark"><img src="{img_src("logo_mark")}" alt="" width="576" height="271"></span><span>SCyPS<small>Center for Smart Cyber-Physical Systems, UMass Lowell</small></span></a>
    <div class="navright">
    <ul class="links" id="menu">{nav}</ul>
    <a class="gift" href="{GIFT_URL}">Make a Gift</a>
    <button class="theme" id="theme" type="button" aria-label="Switch to dark mode"><svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></svg><span class="lbl">Dark</span></button>
    <button class="navtoggle" aria-expanded="false" aria-controls="menu">Menu</button>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
{foot}
{script_html}
</body>
</html>
"""

def build_publications(pubs_section, footer_html, script_html):
    out = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "publications.html")
    body = pubs_section.replace('<section id="publications">', '<section id="publications" class="pubpage">')
    body = body.replace("<h2>", "<h1>", 1).replace("</h2>", "</h1>", 1)
    page = page_shell("Publications | SCyPS, UMass Lowell",
                      f"All {n_pubs} peer-reviewed papers from Center for Smart Cyber-Physical Systems faculty since 2019, searchable and filterable by faculty member, year, and type.",
                      body, footer_html, script_html, active="publications", canonical="publications.html", ld=_ld(ld_articles(P)))
    page = new_tab_links(page)
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out}: {len(page)/1024:.0f} KB")

NL_CSS = (".nlblock{margin:0 0 34px}.nlcard{display:grid;grid-template-columns:150px 1fr;gap:20px;align-items:start;border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:16px 18px;margin:0 0 14px;max-width:760px}"
          ".nlcover img{width:100%;height:auto;border:1px solid var(--line);border-radius:4px}.nlkick{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin:0 0 4px}.nlcard h3{margin:0 0 6px;font-size:22px}.nlcard p{margin:0 0 8px;color:var(--ink-2)}.nlacts a{font-weight:600}"
          ".nlmonthly{font-size:15px;color:var(--ink-2)}.nlissues{display:inline;list-style:none;margin:0;padding:0}.nlissues li{display:inline}.nlissues li+li::before{content:' · ';color:var(--ink-3)}"
          "@media (max-width:640px){.nlcard{grid-template-columns:1fr}.nlcover img{max-width:180px}}")

def newsletter_block():
    """The newsletters, for the top of the News page: the latest print edition with its cover, then the monthly issues."""
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    ndir = os.path.join(root, "newsletters"); pdir = os.path.join(ndir, "print")
    prints = []
    if os.path.isdir(pdir):
        for f in sorted(os.listdir(pdir), reverse=True):
            m = re.fullmatch(r"SCyPS-Newsletter-(\d{4}-\d{2})-Vol(\d+)-No(\d+)\.pdf", f)
            if m: prints.append((m.group(1), m.group(2), m.group(3), f))
    issues = sorted([f[:7] for f in os.listdir(ndir) if re.fullmatch(r"\d{4}-\d{2}\.html", f)], reverse=True) if os.path.isdir(ndir) else []
    if not prints and not issues: return ""
    cards = ""
    for pym, vol, no, f in prints[:2]:
        cov = f'<img src="newsletters/print/{pym}-cover.jpg" alt="" width="240" height="311">' if os.path.exists(os.path.join(pdir, f"{pym}-cover.jpg")) else ""
        cards += (f'<div class="nlcard"><a class="nlcover" href="newsletters/print-{pym}.html">{cov}</a><div><p class="nlkick">Print edition</p>'
                  f'<h3><a href="newsletters/print-{pym}.html">{MONTH_FULL[int(pym[5:7])]} {pym[:4]}</a></h3><p>Volume {vol}, Number {no}: the director&rsquo;s letter, a project, a faculty member, and a student, plus the month&rsquo;s papers and awards.</p>'
                  f'<p class="nlacts"><a href="newsletters/print-{pym}.html">Read online</a> &middot; <a href="newsletters/print/{f}" download>Download PDF</a></p></div></div>')
    monthly = "".join(f'<li><a href="newsletters/{ym}.html">{MONTH_FULL[int(ym[5:7])]} {ym[:4]}</a></li>' for ym in issues[:12])
    return (f'<div class="nlblock" id="newsletters"><h2 class="grouph">Newsletters</h2>{cards}'
            f'<p class="nlmonthly">Monthly issues, generated from the center&rsquo;s records and sent to members and partners: </p><ul class="nlissues">{monthly}</ul></div>')


def build_newspage(footer_html, script_html):
    out = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "news.html")
    window = 3
    items = build_news_items(window)
    while len(items) < 6 and window < 24:
        window += 3
        items = build_news_items(window)
    span = "the last three months" if window == 3 else f"the last {window} months"
    counts = {}
    for it in items: counts[it.get("key", "milestone")] = counts.get(it.get("key", "milestone"), 0) + 1
    chips = '<button class="chip" data-k="all" aria-pressed="true" type="button">All</button>'
    for key, label in [("award", "Awards"), ("journal", "Journals"), ("conference", "Conferences"),
                       ("chapter", "Chapters"), ("presentation", "Presentations"), ("milestone", "Milestones")]:
        n = counts.get(key, 0)
        dis = "" if n else " disabled"
        chips += f'<button class="chip" data-k="{key}" aria-pressed="false" type="button"{dis}>{label} ({n})</button>'

    nl_html = newsletter_block()
    body = f"""<section id="news">
  <div class="wrap">
    <div class="shead"><h1>News</h1><p>The center's newsletter first, then every paper, award, and milestone from {span}, newest first, generated from the center's own record.</p></div>
    {nl_html}
    <div class="newsgrid">
      <div>
        <div class="nfilters" role="group" aria-label="Filter news">
          <span class="lab">Show</span>{chips}
        </div>
        <p class="ncount" id="ncount" aria-live="polite">Showing all {len(items)} items</p>
        <h2 class="grouph vh">Recent items</h2>
        <ol class="timeline plain" id="newslist">{render_news(items)}</ol>
      </div>
      <aside class="stream" aria-label="Latest publications">
        <h2 class="grouph">Latest papers</h2>
        <p class="sub">The {min(24, n_pubs)} most recent, updated with every build.</p>
        <ol>{stream_html()}</ol>
        <p class="foot"><a href="publications.html">All {n_pubs} publications</a> &middot; <a href="#newsletters">Newsletters</a></p>
      </aside>
    </div>
  </div>
</section>"""
    page = page_shell("News | SCyPS, UMass Lowell",
                      "Recent papers, awards, and milestones from the Center for Smart Cyber-Physical Systems at UMass Lowell, with a live list of the newest publications.",
                      body, footer_html, script_html, extra_css=".timeline.plain{list-style:none;margin:0;padding:0}" + NL_CSS, active="news", canonical="news.html")
    page = new_tab_links(page)
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out}: {len(page)/1024:.0f} KB; {len(items)} news items from {span}")



def build_people_pages(filled, footer_html, script_html):
    """filled: dict of already-formatted section markup, one per page."""
    for name, title, desc, active in [
        ("people", "People | SCyPS, UMass Lowell",
         "Faculty, affiliated researchers, and external collaborators of the Center for Smart Cyber-Physical Systems at UMass Lowell.", "people"),
        ("students", "Students | SCyPS, UMass Lowell",
         "Doctoral students in the Advanced Communication Networks Laboratory at UMass Lowell and their research.", "students"),
        ("alumni", "Alumni | SCyPS, UMass Lowell",
         "Ph.D. graduates and postdoctoral alumni of the Advanced Communication Networks Laboratory and where they are now.", "alumni")]:
        out = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", name + ".html")
        body = filled[name]
        if name == "alumni":
            body = body.replace("</section>",
                '<div class="wrap"><div class="giftbox" style="margin-bottom:56px"><h3>Support the next cohort</h3>'
                '<p>Gifts to the center fund student travel to conferences, testbed equipment, and summer research positions.</p>'
                f'<a class="btn-gift" href="{GIFT_URL}">Donate to the Center</a></div></div></section>', 1)
        body = body.replace("<h2>", "<h1>", 1).replace("</h2>", "</h1>", 1)
        page = page_shell(title, desc, body, footer_html, script_html, active=active, canonical=name + ".html",
                          extra_css=COLLAB_CSS if name == "people" else "", ld=_ld(ld_people()) if name == "people" else "")
        page = new_tab_links(page)
        open(out, "w", encoding="utf-8").write(page)
        print(f"wrote {out}: {len(page)/1024:.0f} KB")





def build_feed():
    """feed.xml: the news items as RSS, with a ready-to-post sentence in each description.

    A posting service (Zapier, Make, IFTTT, Hootsuite) polls this file and posts new items to X or
    LinkedIn. Each item carries a category so a rule can post only awards and milestones rather than
    every paper. The description is already written to fit a post, under 270 characters plus the link.
    """
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    items = build_news_items(12)[:40]
    def post_text(it):
        t = re.sub(r"\s+", " ", it.get("post") or f'{it["title"]}. {it["body"]}').strip()
        if not t.endswith((".", "!", "?")): t += "."
        return (t[:264].rsplit(" ", 1)[0].rstrip(",;:") + "...") if len(t) > 267 else t
    MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    def entry(it):
        y, m = it["ym"]
        # RSS wants a full date; the first of the month is the honest approximation for a monthly item
        pub = f"{MON[m]} {y} 00:00:00 +0000"
        link = it.get("link") or (SITE_URL + "news.html")
        return (
            "  <item>\n"
            f"    <title>{esc(it['title'])}</title>\n"
            f"    <link>{esc(link)}</link>\n"
            f"    <guid isPermaLink=\"false\">scyps-{y}-{m:02d}-{hashlib.md5(it['title'].encode()).hexdigest()[:10]}</guid>\n"
            f"    <category>{esc(it['kind'])}</category>\n"
            f"    <pubDate>01 {pub}</pubDate>\n"
            f"    <description>{esc(post_text(it))}</description>\n"
            "  </item>\n")
    out = [entry(it) for it in items]
    def wrap(body, title, path, desc):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
                f"  <title>{title}</title>\n"
                f"  <link>{SITE_URL}news.html</link>\n"
                f"  <description>{desc}</description>\n"
                "  <language>en-us</language>\n"
                f'  <atom:link href="{SITE_URL}{path}" rel="self" type="application/rss+xml"/>\n'
                + body + "</channel>\n</rss>\n")

    open(os.path.join(root, "feed.xml"), "w", encoding="utf-8").write(
        wrap("".join(out), "SCyPS news", "feed.xml",
             "Papers, awards, and milestones from the Center for Smart Cyber-Physical Systems at UMass Lowell."))

    # A pre-filtered feed for auto-posting: awards, milestones, and talks, not every paper. A posting
    # service on a free plan cannot add a filter step, so the filtering happens here instead.
    HIGHLIGHT = {"award", "milestone", "presentation"}
    hi = [entry(it) for it in items if it["key"] in HIGHLIGHT]
    open(os.path.join(root, "feed-highlights.xml"), "w", encoding="utf-8").write(
        wrap("".join(hi), "SCyPS highlights", "feed-highlights.xml",
             "Awards, milestones, and talks from the Center for Smart Cyber-Physical Systems at UMass Lowell."))
    print(f"wrote feed.xml: {len(items)} items; feed-highlights.xml: {len(hi)} items")



SPOTLIGHTS = _load_overlay("spotlights.json", {"entries": []}).get("entries", [])

def _spotlight_students(sp):
    """STUDENTS entries for the people named in a spotlight, so we can show their photos and status."""
    by = {s["name"]: s for s in STUDENTS}
    return [by.get(n, {"name": n, "status": "", "advisor": sp.get("advisor", "")}) for n in sp["students"]]

def spotlight_label(sp):
    y, m = int(sp["ym"][:4]), int(sp["ym"][5:7]); return f"{MONTH_FULL[m]} {y}"

def spotlight_article(sp, full=True):
    """One spotlight as HTML: the students, the story, the papers. full=False gives the teaser used on Students."""
    who = _spotlight_students(sp)
    heads = "".join(f'<div class="spwho">{stu_avatar(s)}<div><b>{esc(s["name"])}</b><span>{esc(s.get("status", ""))}</span></div></div>' for s in who)
    if not full:
        return (f'<article class="spteaser"><p class="spkicker">Student spotlight, {esc(spotlight_label(sp))}</p><h3><a href="spotlight.html#{esc(sp["ym"])}">{esc(sp["title"])}</a></h3>'
                f'<p>{esc(sp["deck"])}</p><div class="spwhos">{heads}</div></article>')
    body = "".join((f'<h3>{esc(s["h"])}</h3>' if s.get("h") else "") + "".join(f"<p>{esc(t)}</p>" for t in s["p"]) for s in sp["sections"])
    papers = "".join(f'<li><a href="https://doi.org/{esc(p["doi"])}">{esc(p["title"])}</a><span class="v">{esc(p.get("note", ""))}</span></li>' for p in sp.get("papers", []))
    links = "".join(f'<li><a href="{esc(l["url"])}">{esc(l["label"])}</a></li>' for l in sp.get("links", []))
    adv = f'<p class="spadv">Advised by {esc(sp["advisor"])}' + (f', {esc(sp["lab"])}' if sp.get("lab") else "") + "</p>"
    fund = f'<p class="spfund">{esc(sp["funding"])}</p>' if sp.get("funding") else ""
    return (f'<article class="spot" id="{esc(sp["ym"])}"><p class="spkicker">Student spotlight, {esc(spotlight_label(sp))}</p><h2>{esc(sp["title"])}</h2>'
            f'<p class="spdeck">{esc(sp["deck"])}</p><div class="spwhos">{heads}</div>{adv}<div class="spbody">{body}</div>'
            + (f'<h3>The papers</h3><ul class="ipubs">{papers}</ul>' if papers else "") + (f'<ul class="splinks">{links}</ul>' if links else "") + fund + "</article>")

def build_spotlight(footer_html, script_html):
    """spotlight.html: the monthly student spotlight, newest first, from spotlights.json."""
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    sps = sorted(SPOTLIGHTS, key=lambda s: s["ym"], reverse=True)
    arts = "".join(spotlight_article(sp) for sp in sps)
    body = f'''<section>
  <div class="wrap">
    <div class="shead"><h1>Student spotlight</h1><p>Each month the center tells one story about its doctoral students: what they built, why it matters, and where to read the work. Faculty nominate students by writing to the director.</p></div>
    <div class="spots">{arts if arts else "<p>The first spotlight is on its way.</p>"}</div>
  </div>
</section>'''
    css = '''
.spots{max-width:46em}.spot{padding:0 0 36px;margin:0 0 36px;border-bottom:1px solid var(--line)}.spot:last-child{border-bottom:0}
.spkicker{font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin:0 0 6px}
.spot h2{margin:0 0 8px}.spdeck{font-size:19px;line-height:1.45;color:var(--ink-2);margin:0 0 18px}
.spwhos{display:flex;flex-wrap:wrap;gap:12px 28px;margin:0 0 8px}.spwho{display:flex;align-items:center;gap:12px}
.spwho .avatar{width:64px;height:64px;border-radius:50%;object-fit:cover}.spwho b{display:block;font-size:16px}.spwho span{font-size:13.5px;color:var(--ink-3)}
.spadv{font-size:14px;color:var(--ink-3);margin:0 0 18px}.spbody h3{font-size:19px;margin:22px 0 8px}.spbody p{font-size:16.5px;line-height:1.6;margin:0 0 12px}
.spot .ipubs{list-style:none;margin:0 0 12px;padding:0}.spot .ipubs li{margin:0 0 8px;font-size:15px;line-height:1.4}.spot .ipubs .v{display:block;color:var(--ink-3);font-size:13.5px}
.splinks{list-style:none;margin:0 0 12px;padding:0;font-size:15px}.spfund{font-size:13.5px;color:var(--ink-3);margin:14px 0 0}
'''
    page = page_shell("Student spotlight | SCyPS, UMass Lowell", "The center's monthly student spotlight: one story a month about what its doctoral students built and why it matters.",
                      body, footer_html, script_html, extra_css=css, active="students", canonical="spotlight.html")
    page = new_tab_links(page)
    open(os.path.join(root, "spotlight.html"), "w", encoding="utf-8").write(page)
    print(f"wrote spotlight.html: {len(sps)} spotlight(s)")


def build_labs(footer_html, script_html):
    """One page listing the laboratories and instruments behind the center's work."""
    out = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "labs.html")
    people = {}
    for grp in ("director", "core", "affiliated", "external"):
        for p in ([FACULTY[grp]] if grp == "director" else FACULTY[grp]):
            people[p["name"]] = p
    cards = ""
    for i, lab in enumerate(LABS):
        offers = "".join(f"<li>{esc(o)}</li>" for o in lab["offers"])
        _acnl = lab["name"].startswith("Advanced Communication Networks Laboratory")   # the lab's links open in a new tab
        links = " ".join(f'<a href="{esc(u)}"' + (' target="_blank" rel="noopener"' if _acnl else "") + f'>{esc(t)}</a>' for t, u in lab["links"])
        lead = people.get(lab["lead"].split(",")[0].strip())
        face = avatar(lead, "sm") if lead else ""
        cards += f"""<article class="lab">
  <div class="labart">{LAB_ART.get(lab["art"], ART.get(lab["art"], ""))}</div>
  <div class="labbody">
    <h2>{esc(lab["name"])}</h2>
    <p class="labwho">{face}<span><b>{esc(lab["lead"])}</b><small>{esc(lab["dept"])}</small></span></p>
    <p class="labwhat">{esc(lab["what"])}</p>
    <h3>What it offers collaborators</h3>
    <ul class="laboffers">{offers}</ul>
    <p class="lablinks">{links}</p>
  </div>
</article>"""
    body = f"""<section id="labs">
  <div class="wrap">
    <div class="shead"><h1>Labs and facilities</h1><p>The center is not a building. It is a set of laboratories and instruments across four UMass Lowell colleges, run by the faculty listed on each one, and open to collaborators on the terms described below.</p></div>
    <div class="facgrid">{cards}</div>
    <div class="ack" style="margin-top:44px">
      <p>Researchers outside UMass Lowell who want time on an instrument, and companies looking for a testbed or a co-op pipeline, should write to the director at <a href="mailto:Vinod_Vokkarane@uml.edu">Vinod_Vokkarane@uml.edu</a> or to the faculty member who runs the facility.</p>
    </div>
  </div>
</section>"""
    css = """.facgrid{display:grid;gap:22px}
.lab{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:stretch;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}
.labart{background:#FFFFFF;justify-content:center;padding:26px;--bg-2:#F3F7FA;--surface:#FFFFFF;--line:#D5DCE5;--ink:#0E2036;--ink-3:#5B6B82;--signal:#0A777F;--brand-blue:#044978;--green:#3BA995;display:flex;align-items:center;padding:18px;border-right:1px solid var(--line)}
.labart svg{width:100%;height:auto;display:block}
.labbody{padding:26px 28px}
.labbody h2{font-size:23px;line-height:1.25;margin-bottom:12px}
.labwho{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.labwho .avatar{width:48px;height:48px;border-radius:8px;flex:none}
.labwho b{display:block;font-size:14.5px}
.labwho small{display:block;font-size:12.5px;color:var(--ink-3)}
.labwhat{font-size:15.5px;color:var(--ink-2);margin-bottom:18px}
.labbody h3{font-size:15px;letter-spacing:.02em;text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
.laboffers{margin:0 0 16px;padding-left:20px}
.laboffers li{font-size:14.5px;color:var(--ink-2);margin-bottom:6px}
.lablinks a{font-size:14.5px;margin-right:18px}
@media (max-width:860px){.lab{grid-template-columns:1fr}.labart{border-right:0;border-bottom:1px solid var(--line)}}
.labart .s-ink{stroke:var(--ink)}
.labart .f-ink{fill:var(--ink)}
.labart .f-surface{fill:var(--surface)}
.labart .f-muted{fill:var(--ink-3)}
.labart .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}

.labart .f-alert{fill:#E25555}
.labart .s-alert{stroke:#E25555}
.labart .f-alert-tint{fill:#FDECEC}

.labart .s-sig{stroke:var(--signal)}
.labart .f-sig{fill:var(--signal)}
.labart .f-brand{fill:var(--brand-blue)}
.labart .s-brand{stroke:var(--brand-blue)}
.labart .f-grn{fill:var(--green)}
.labart .s-grn{stroke:var(--green)}
.labart .f-tint{fill:var(--bg-2)}
.labart .s-line{stroke:var(--line)}
.labart .f-line{fill:var(--line)}
.labart .f-sigt{fill:var(--signal-tint)}
.labart .f-amb{fill:var(--amber)}
.labart .s-amb{stroke:var(--amber)}
.labart .s-muted{stroke:var(--ink-3)}"""
    page = page_shell("Labs and facilities | SCyPS, UMass Lowell",
                      "The laboratories and instruments behind the Center for Smart Cyber-Physical Systems at UMass Lowell, and what each can offer collaborators.",
                      body, footer_html, script_html, extra_css=css, active="labs", canonical="labs.html")
    page = new_tab_links(page)
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out}: {len(page)/1024:.0f} KB; {len(LABS)} labs")





def alumni_profile_card(name, p):
    photo = IMG.get("alum_" + p["slug"]) or IMG.get("head_" + {"islam": "zahidul", "edib": "shamsun"}.get(p["slug"], "-"))
    if photo:
        fig = f'<img class="alumpic" src="data:image/jpeg;base64,{photo}" alt="{esc(name)}" width="160" height="160">'
    else:
        ini = "".join(w[0] for w in name.replace("-", " ").split()[:2]).upper()
        fig = f'<div class="alumpic mono" aria-hidden="true">{esc(ini)}</div>'
    inst = f' <span class="alinst">{esc(p["inst"])}</span>' if p.get("inst") else ""
    era = f' <span class="alinst">{esc(p["era"])}</span>' if p.get("era") else ""
    links = []
    if p.get("web"): links.append(f'<a href="{esc(p["web"])}">Profile</a>')
    if p.get("scholar"): links.append(f'<a href="https://scholar.google.com/citations?user={esc(p["scholar"])}&amp;hl=en">Google Scholar</a>')
    if p.get("linkedin"): links.append(f'<a href="{esc(p["linkedin"])}">LinkedIn</a>')
    gs = scholar_line(name)
    org = (", " + esc(p["org"])) if p.get("org") else ""
    return (f'<article class="alum"><div class="alumhead">{fig}<div><h3>{esc(name)}</h3>'
            f'<p class="aldeg">{esc(p["degree"])}{inst}{era}</p><p class="alrole"><b>{esc(p["role"])}</b>{org}</p></div></div>'
            f'<p class="alpath">{esc(p["path"])}</p><p class="alfocus">{esc(p["focus"])}</p>'
            + (f'<p class="pmeta">' + " ".join(f'<span class="mi">{l}</span>' for l in links) + '</p>' if links else "")
            + (f'<p class="gsline">{gs}</p>' if gs else "") + '</article>')

def alumni_profiles_html():
    phd = [n for n, p in ALUMNI_PROFILES.items() if p["degree"].startswith("Ph.D.")]
    pd = [n for n, p in ALUMNI_PROFILES.items() if not p["degree"].startswith("Ph.D.")]
    phd.sort(key=lambda n: -int(ALUMNI_PROFILES[n]["degree"].split()[1][:4]))
    return ("".join(alumni_profile_card(n, ALUMNI_PROFILES[n]) for n in phd),
            "".join(alumni_profile_card(n, ALUMNI_PROFILES[n]) for n in pd))

# ---------------------------------------------------------------- structured data (schema.org JSON-LD)
# Machine-readable descriptions search engines use for knowledge panels and rich results. The center
# is an Organization; every roster member a Person with ORCID and Scholar identifiers; every paper a
# ScholarlyArticle; SUMMIT a ResearchProject; the postdoc a JobPosting. All from the same records as
# the visible pages, so they cannot disagree with what a reader sees.
def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"

def ld_organization():
    members = []
    for grp in ("director", "core", "affiliated"):
        for p in ([FACULTY[grp]] if grp == "director" else FACULTY[grp]):
            members.append({"@type": "Person", "name": re.sub(r"\s*\(.*?\)", "", p["name"]).strip(), "url": f"{SITE_URL}people.html"})
    return {"@context": "https://schema.org", "@type": "ResearchOrganization", "@id": f"{SITE_URL}#org",
            "name": "Center for Smart Cyber-Physical Systems", "alternateName": "SCyPS", "url": SITE_URL,
            "logo": f"{SITE_URL}logo-mark.png", "image": f"{SITE_URL}og-card.png", "foundingDate": "2019-10-01",
            "description": "A university research center at UMass Lowell on the security and resilience of the sensing, "
                           "networking, AI, and control loop that runs power grids, transportation networks, and health infrastructure.",
            "parentOrganization": {"@type": "CollegeOrUniversity", "name": "University of Massachusetts Lowell",
                                   "url": "https://www.uml.edu/", "sameAs": "https://www.wikidata.org/wiki/Q7894205"},
            "address": {"@type": "PostalAddress", "streetAddress": "1 University Ave.", "addressLocality": "Lowell",
                        "addressRegion": "MA", "postalCode": "01854", "addressCountry": "US"},
            "email": "Vinod_Vokkarane@uml.edu", "telephone": "+1-978-934-3345",
            "founder": [{"@type": "Person", "name": n} for n in ["Vinod M. Vokkarane", "Martin Margala", "Yan Luo", "Sukesh Aghara", "Yuanchang Xie"]],
            "employee": {"@type": "Person", "name": "Vinod M. Vokkarane", "jobTitle": "Director",
                         "sameAs": [f"https://orcid.org/{ORCID['Vinod M. Vokkarane']}", f"https://scholar.google.com/citations?user={SCHOLAR['Vinod M. Vokkarane']}"]},
            "member": members,
            "knowsAbout": [t for _, t, _, _ in THRUSTS]}

def ld_people():
    out = []
    for grp in ("director", "core", "affiliated", "external"):
        for p in ([FACULTY[grp]] if grp == "director" else FACULTY[grp]):
            name = re.sub(r"\s*\(.*?\)", "", p["name"]).strip()
            same = []
            if ORCID.get(p["name"]): same.append(f"https://orcid.org/{ORCID[p['name']]}")
            if SCHOLAR.get(p["name"]): same.append(f"https://scholar.google.com/citations?user={SCHOLAR[p['name']]}")
            if LINKEDIN.get(p["name"]): same.append(LINKEDIN[p["name"]])
            if p.get("url"): same.append(p["url"])
            org = p.get("inst") if p.get("inst") not in (None, "Lowell") else "University of Massachusetts Lowell"
            person = {"@type": "Person", "name": name, "jobTitle": p.get("title", ""),
                      "affiliation": {"@type": "Organization", "name": org or "University of Massachusetts Lowell"},
                      "memberOf": {"@id": f"{SITE_URL}#org"}, "sameAs": same}
            if p.get("email"): person["email"] = p["email"]
            if p.get("areas"): person["knowsAbout"] = [a.strip() for a in re.split(r"[;,]", p["areas"]) if a.strip()][:8]
            out.append(person)
    return {"@context": "https://schema.org", "@graph": out}

def ld_articles(papers):
    out = []
    for p in papers:
        authors = p["authors"] if isinstance(p["authors"], list) else [a.strip() for a in p["authors"].split(",")]
        a = {"@type": "ScholarlyArticle", "headline": p["title"], "author": [{"@type": "Person", "name": n} for n in authors],
             "datePublished": str(p["year"]), "isPartOf": {"@type": "Periodical" if p["type"] == "journal" else "Event", "name": p["venue"]}}
        if p.get("doi"): a["sameAs"] = f"https://doi.org/{p['doi']}"; a["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": p["doi"]}
        out.append(a)
    return {"@context": "https://schema.org", "@graph": out}

def ld_summit():
    return {"@context": "https://schema.org", "@type": "ResearchProject", "name": "SUMMIT: A Secure and Resilient Multi-site Smart Grid Testbed for Multidisciplinary Research and Training",
            "alternateName": "SUMMIT", "url": f"{SITE_URL}summit.html", "startDate": "2026-10-01", "endDate": "2029-09-30",
            "funding": {"@type": "Grant", "identifier": "2511635", "name": "NSF Major Research Instrumentation Track 2",
                        "funder": {"@type": "Organization", "name": "National Science Foundation", "url": "https://www.nsf.gov/"}},
            "parentOrganization": {"@id": f"{SITE_URL}#org"},
            "member": [{"@type": "Organization", "name": n} for n in ["University of Massachusetts Lowell", "NYU Tandon School of Engineering", "West Virginia University"]],
            "description": "A federated cyber-physical testbed linking RTDS real-time simulation of the Northeast transmission grid with control, networking, and cybersecurity hardware in the loop across three universities, delivered as hardware-in-the-loop Simulation-as-a-Service."}

def ld_jobs():
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "JobPosting", "title": "Fully funded M.S. Research Assistantship (BOND-AI, ARPO, ARPO-Sensor Fusion), U.S. citizens only",
         "description": "Tuition and stipend for a master's degree in electrical or computer engineering at UMass Lowell while working on BOND-AI (NextFlex), ARPO (U.S. Army), or ARPO-Sensor Fusion (Massachusetts Technology Collaborative). U.S. citizenship required by the sponsors.",
         "datePosted": "2026-09-21", "employmentType": ["FULL_TIME", "INTERN"], "url": f"{SITE_URL}positions.html", "directApply": False,
         "eligibilityToWorkRequirement": "U.S. citizenship required",
         "hiringOrganization": {"@type": "Organization", "name": "University of Massachusetts Lowell", "sameAs": "https://www.uml.edu/"},
         "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "streetAddress": "1 University Ave.", "addressLocality": "Lowell", "addressRegion": "MA", "postalCode": "01854", "addressCountry": "US"}},
         "industry": "Research", "occupationalCategory": "Graduate Research Assistant"},
        {"@type": "JobPosting", "title": "Postdoctoral Research Associate, SUMMIT federated smart grid testbed",
         "description": "Lead federation development for SUMMIT, a three-university federated smart grid cybersecurity testbed funded by the NSF Major Research Instrumentation program.",
         "datePosted": "2026-09-01", "employmentType": "FULL_TIME", "url": POSTDOC_URL, "directApply": True,
         "hiringOrganization": {"@type": "Organization", "name": "University of Massachusetts Lowell", "sameAs": "https://www.uml.edu/"},
         "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "streetAddress": "1 University Ave.", "addressLocality": "Lowell", "addressRegion": "MA", "postalCode": "01854", "addressCountry": "US"}},
         "industry": "Research", "occupationalCategory": "Postdoctoral Researcher"}]}


# ---------------------------------------------------------------- open positions
# Everything a candidate needs, one page, at a stable URL. Edit POSITIONS to add or close a role.
POSITIONS = [
    {"kind": "Postdoctoral researcher", "title": "Postdoctoral Research Associate, SUMMIT federated smart grid testbed",
     "group": "Advanced Communication Networks Laboratory (Vokkarane)", "status": "Open",
     "what": "Lead federation development for SUMMIT across UMass Lowell, NYU Tandon, and West Virginia University: real-time simulation with hardware in the loop, a wide-area software-defined network, and the access model that opens the instrument to outside groups.",
     "want": "A Ph.D. in electrical or computer engineering or computer science; experience with power system simulation (RTDS or OPAL-RT), SDN, or cyber-physical security; the appetite to run an instrument, not only a study.",
     "apply": POSTDOC_URL, "apply_label": "Apply through UMass Lowell careers"},
    {"kind": "M.S. research assistantships", "title": "Fully funded M.S. research assistantships on BOND-AI, ARPO, and ARPO-Sensor Fusion (U.S. citizens only)",
     "group": "Advanced Communication Networks Laboratory (Vokkarane), with the BOND-AI team (Akyurtlu, Ranasingha, Stapleton)", "status": "Open",
     "what": "Tuition and a stipend for a master's degree in electrical or computer engineering while working on one of three funded projects: BOND-AI, a NextFlex program on physics-informed AI for qualifying printed interfaces and bond joints that must survive 500 \u00b0C; ARPO, a U.S. Army project on autonomous robotic planning and optimization over contested networks; or ARPO-Sensor Fusion, a Massachusetts Technology Collaborative project on AI models that fuse multi-sensor intelligence feeds for autonomous missions, performed at UMLARC.",
     "want": "U.S. citizenship, which the sponsors require. A B.S. in ECE, CS, mechanical engineering, or materials science; strength in at least one of machine learning, embedded systems, robotics, or materials characterization; the ability to start in spring or fall 2027. Say which project you want and why.",
     "apply": "mailto:Vinod_Vokkarane@uml.edu?subject=M.S.%20research%20assistantship%20(BOND-AI%20%2F%20ARPO)", "apply_label": "Write to the director with a CV"},
    {"kind": "Doctoral students", "title": "Ph.D. positions across the center's thrusts",
     "group": "Any center faculty member", "status": "Rolling",
     "what": "Funded doctoral positions open as awards start. Current areas with funding: smart grid cybersecurity and restoration, multi-band optical networking and FUSION, fault-tolerant edge computing, hardware security, high performance computing and data integrity, connected transportation, and AI for cyber-physical control.",
     "want": "A strong M.S. or B.S. in ECE, CS, or a related field. Research experience matters more than the school's name. Write to the faculty member whose work matches yours and copy the director; say which paper of theirs made you write.",
     "apply": "https://www.uml.edu/grad/", "apply_label": "UMass Lowell graduate admissions"},
    {"kind": "Undergraduate researchers", "title": "Research positions for UMass Lowell undergraduates",
     "group": "Any center laboratory", "status": "Rolling",
     "what": "Paid and for-credit research in the center's laboratories, including NSF REU supplements when available, and senior capstone projects sponsored through the center.",
     "want": "Juniors and seniors in engineering or computing with the relevant coursework; write to the laboratory's faculty lead.",
     "apply": "mailto:Vinod_Vokkarane@uml.edu?subject=Undergraduate%20research%20with%20the%20center", "apply_label": "Write to the director"},
    {"kind": "Visiting scholars and industry residents", "title": "Visiting positions on the SUMMIT testbed",
     "group": "SUMMIT (Vokkarane)", "status": "From 2027",
     "what": "As SUMMIT opens to collaborators, visiting researchers and engineers from utilities, vendors, and agencies can hold instrument time and a desk at UMass Lowell for a semester.",
     "want": "A defined experiment and a home institution or company that supports the visit. Write to the director to scope it.",
     "apply": "mailto:Vinod_Vokkarane@uml.edu?subject=Visiting%20position%20on%20SUMMIT", "apply_label": "Write to the director"},
]

def build_positions(footer_html, script_html):
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    cards = "".join(
        f'<article class="pos"><div class="poshead"><span class="poskind">{esc(p["kind"])}</span>'
        f'<span class="posstatus {"open" if p["status"] == "Open" else ""}">{esc(p["status"])}</span></div>'
        f'<h2>{esc(p["title"])}</h2><p class="posgroup">{esc(p["group"])}</p>'
        f'<h3>The work</h3><p>{esc(p["what"])}</p><h3>Who we are looking for</h3><p>{esc(p["want"])}</p>'
        f'<p class="posapply"><a class="btn" href="{esc(p["apply"])}">{esc(p["apply_label"])}</a></p></article>'
        for p in POSITIONS)
    body = f"""<section>
  <div class="wrap">
    <div class="shead"><h1>Open positions</h1><p>Postdoctoral, doctoral, undergraduate, and visiting positions with the center's faculty and laboratories. Students who join work on real instruments and real data, publish, and leave with an employer already in the room.</p></div>
    <div class="poslist">{cards}</div>
    <p class="posnote">Every position at UMass Lowell is filled through the university's own processes; the center connects candidates with faculty. UMass Lowell is an equal opportunity employer.</p>
  </div>
</section>"""
    css = """.poslist{display:grid;gap:22px;max-width:52em}
.pos{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px 26px}
.poshead{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:8px}
.poskind{font-size:12.5px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3)}
.posstatus{font-size:12.5px;font-weight:600;padding:3px 10px;border-radius:999px;background:var(--bg-2);color:var(--ink-2)}
.posstatus.open{background:var(--green);color:#062B24}
.pos h2{font-size:21px;margin:0 0 4px}.posgroup{color:var(--ink-3);font-size:14px;margin:0 0 14px}
.pos h3{font-size:13px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3);margin:14px 0 4px}
.pos p{margin:0;font-size:15.5px;line-height:1.55}
.posapply{margin-top:16px!important}.pos .btn{display:inline-block;background:var(--ink);color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-size:14.5px}
.posnote{font-size:13.5px;color:var(--ink-3);margin-top:28px;max-width:52em}"""
    page = page_shell("Open positions | SCyPS, UMass Lowell",
                      "Postdoctoral, doctoral, undergraduate, and visiting positions at the Center for Smart Cyber-Physical Systems, UMass Lowell.",
                      body, footer_html, script_html, extra_css=css, active="positions", canonical="positions.html", ld=_ld(ld_jobs()))
    open(os.path.join(root, "positions.html"), "w", encoding="utf-8").write(new_tab_links(page))
    print("wrote positions.html:", len(POSITIONS), "positions")

# ---------------------------------------------------------------- monthly newsletter
# One issue per calendar month, built from the publication, award, and news records. Three outputs:
#   newsletters/YYYY-MM.html        the web issue, in the site's design, listed in newsletters/index.html
#   newsletters/YYYY-MM-email.html  the same issue as an email (tables, inline styles, hosted images)
#   newsletters/YYYY-MM.txt         plain text, for a mailing list that wants it
# The workflow builds the previous month on the first of each month; --newsletter YYYY-MM builds any month.
MONTH_FULL = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def _month_items(y, m):
    """Everything dated in one calendar month: papers, awards that started, hand-written news."""
    papers = [p for p in P if p["year"] == y and (month_of(p) or 0) == m]
    papers.sort(key=lambda p: (p["type"] != "journal", p["title"].lower()))
    awards = [pr for pr in PROJECTS if _period_start(pr.get("period", "")) == (y, m)]
    notes = []
    for when, text in NEWS:
        mm = re.match(r"([A-Za-z]{3})[a-z]*\s+(\d{4})", when)
        if not mm: continue
        mon = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}.get(mm.group(1))
        if (int(mm.group(2)), mon) == (y, m): notes.append(text)
    # drop a note that only restates an award listed above
    awards_words = [set(re.findall(r"[A-Za-z]{4,}", pr["title"].lower())[:6]) for pr in awards]
    notes = [t for t in notes if not any(len(set(re.findall(r"[A-Za-z]{4,}", t.lower())[:8]) & w) >= 3 for w in awards_words)]
    upcoming = [pr for pr in PROJECTS if _period_start(pr.get("period", "")) == ((y + (m == 12)), (m % 12) + 1)]
    return papers, awards, notes, upcoming

def _author_html(authors, bold=True):
    names = authors if isinstance(authors, list) else [a.strip() for a in authors.split(",")]
    out = []
    for a in names:
        sur = a.split()[-1] if a.split() else a
        out.append(f"<b>{esc(a)}</b>" if bold and sur in CENTER_AUTHORS else esc(a))
    return ", ".join(out)

def build_newsletter(ym, footer_html, script_html):
    y, m = int(ym[:4]), int(ym[5:7])
    label = f"{MONTH_FULL[m]} {y}"
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    ndir = os.path.join(root, "newsletters"); os.makedirs(ndir, exist_ok=True)
    papers, awards, notes, upcoming = _month_items(y, m)
    journal = [p for p in papers if p["type"] == "journal"]
    logo = f"{SITE_URL}logo-mark.png"

    # ---- the opening line writes itself from the counts
    bits = []
    if awards: bits.append(f"{len(awards)} new award{'s' if len(awards) != 1 else ''}")
    if papers: bits.append(f"{len(papers)} new paper{'s' if len(papers) != 1 else ''}" + (f", {len(journal)} in journals" if journal else ""))
    if notes: bits.append(f"{len(notes)} milestone{'s' if len(notes) != 1 else ''}")
    lead = (f"{label} at the center: " + ", ".join(bits) + ".") if bits else f"A quiet month at the center: no new papers or awards were recorded for {label}."

    # ---- shared section content, rendered twice (web and email)
    def paper_block(p, email=False):
        doi = f'https://doi.org/{p["doi"]}' if p.get("doi") else ""
        title = f'<a href="{esc(doi)}" style="color:#044978;text-decoration:none">{esc(p["title"])}</a>' if doi else esc(p["title"])
        chip = "" if email else journal_chip(p["venue"]) if p["type"] == "journal" else ""
        return (f'<p style="margin:0 0 14px;font-size:15px;line-height:1.45;color:#0E2036">{_author_html(p["authors"])}<br>'
                f'{title}<br><span style="color:#5B6B82;font-size:13.5px"><i>{esc(p["venue"])}</i>, {esc(p["details"])}</span>{chip}</p>')
    def award_block(pr):
        amt = f' <span style="color:#5B6B82">({esc(pr["amount"])})</span>' if pr.get("amount") else ""
        return (f'<p style="margin:0 0 14px;font-size:15px;line-height:1.45;color:#0E2036"><b>{esc(pr["title"])}</b>{amt}<br>'
                f'<span style="color:#5B6B82;font-size:13.5px">{esc(pr["sponsor"])}. {esc(pr["team"])}</span><br>{esc(pr["desc"])}</p>')
    def note_block(t):
        return f'<p style="margin:0 0 14px;font-size:15px;line-height:1.45;color:#0E2036">{esc(t)}</p>'

    def sections(email):
        h = []
        def head(t): h.append(f'<h2 style="font-family:Georgia,serif;font-size:20px;margin:26px 0 12px;color:#044978;border-bottom:1px solid #D5DCE5;padding-bottom:6px">{t}</h2>')
        h.append(f'<p style="font-size:17px;line-height:1.5;color:#0E2036;margin:0 0 8px">{esc(lead)}</p>')
        if awards:
            head("New awards"); h += [award_block(pr) for pr in awards]
        if papers:
            head("New papers")
            if journal:
                h.append('<p style="font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:#5B6B82;margin:0 0 8px">Journal articles</p>')
                h += [paper_block(p, email) for p in journal]
            conf = [p for p in papers if p["type"] != "journal"]
            if conf:
                h.append('<p style="font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:#5B6B82;margin:10px 0 8px">Conference papers and chapters</p>')
                h += [paper_block(p, email) for p in conf]
        sp = next((s for s in SPOTLIGHTS if s["ym"] == ym), None)
        if sp:
            head("Student spotlight")
            names = " and ".join(sp["students"])
            h.append(f'<p style="margin:0 0 14px;font-size:15px;line-height:1.45;color:#0E2036"><b>{esc(sp["title"])}</b>: {esc(names)}.<br>{esc(sp["deck"])}<br>'
                     f'<a href="{SITE_URL}spotlight.html#{esc(sp["ym"])}" style="color:#044978">Read the spotlight</a></p>')
        if notes:
            head("Milestones"); h += [note_block(t) for t in notes]
        if upcoming:
            head("Coming up")
            h += [f'<p style="margin:0 0 10px;font-size:15px;color:#0E2036"><b>{esc(pr["title"])}</b> starts {esc(pr["period"].split(" to ")[0].split(",")[0])}.</p>' for pr in upcoming]
        head("Work with us")
        h.append('<p style="margin:0 0 10px;font-size:15px;line-height:1.45;color:#0E2036">Doctoral applicants: write to the faculty member whose work matches yours and copy the director. '
                 f'Companies and agencies: the <a href="{SITE_URL}labs.html" style="color:#044978">laboratories page</a> lists what each facility can offer, and the '
                 f'<a href="{SITE_URL}summit.html" style="color:#044978">SUMMIT testbed</a> opens to collaborators in 2026 to 2027.</p>')
        return "".join(h)

    # ---- web issue
    body = f"""<section>
  <div class="wrap">
    <p class="crumb"><a href="../news.html#newsletters">Newsletters</a></p>
    <div class="shead"><h1>{esc(label)}</h1><p>The center's monthly note: what its faculty and students published, what was funded, and what is next. Generated from the center's own records.</p></div>
    <div class="nlbody">{sections(False)}</div>
    <p class="nlfoot">This issue was generated on {esc(datetime.date.today().strftime("%B %d, %Y"))} from the same records that produce the <a href="../news.html">news page</a>. Subscribe to the <a href="../feed.xml">feed</a> to receive items as they appear.</p>
  </div>
</section>"""
    css = ".nlbody{max-width:44em}.nlbody h2{font-size:20px}.crumb{font-size:14px;margin-bottom:12px}.nlfoot{font-size:13.5px;color:var(--ink-3);margin-top:34px;max-width:44em}"
    global FONT_ROOT
    FONT_ROOT = "../"
    page = page_shell(f"{label} newsletter | SCyPS, UMass Lowell",
                      f"The Center for Smart Cyber-Physical Systems monthly newsletter for {label}: new papers, awards, and milestones.",
                      body, footer_html, script_html, extra_css=css, active="news", canonical=f"newsletters/{ym}.html")
    page = page.replace('href="index.html', 'href="../index.html').replace('href="people.html', 'href="../people.html') \
               .replace('href="students.html', 'href="../students.html').replace('href="alumni.html', 'href="../alumni.html') \
               .replace('href="publications.html', 'href="../publications.html').replace('href="news.html', 'href="../news.html') \
               .replace('href="insights.html', 'href="../insights.html').replace('href="positions.html', 'href="../positions.html') \
               .replace('href="labs.html', 'href="../labs.html').replace('href="summit.html', 'href="../summit.html') \
               .replace('href="spotlight.html', 'href="../spotlight.html') \
               .replace('href="../index.html">Newsletters', 'href="index.html">Newsletters')
    page = re.sub(r'href="research-(\w+)\.html', r'href="../research-\1.html', page)
    page = new_tab_links(page)
    open(os.path.join(ndir, f"{ym}.html"), "w", encoding="utf-8").write(page)
    FONT_ROOT = ""

    # ---- email issue: tables, inline styles, hosted logo, no scripts
    email = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>SCyPS newsletter, {esc(label)}</title></head>
<body style="margin:0;padding:0;background:#F3F7FA;font-family:Arial,Helvetica,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F3F7FA"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#FFFFFF;border:1px solid #D5DCE5;border-radius:12px">
  <tr><td style="background:#044978;border-radius:12px 12px 0 0;padding:22px 28px">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td style="padding-right:14px"><img src="{logo}" width="64" height="30" alt="" style="display:block"></td>
      <td><div style="color:#FFFFFF;font-size:18px;font-weight:bold">Center for Smart Cyber-Physical Systems</div>
          <div style="color:#C9DCEA;font-size:13px">University of Massachusetts Lowell &middot; {esc(label)}</div></td></tr></table>
  </td></tr>
  <tr><td style="padding:26px 28px 8px">{sections(True)}</td></tr>
  <tr><td style="padding:18px 28px 26px;border-top:1px solid #D5DCE5;color:#5B6B82;font-size:12.5px;line-height:1.5">
    You are receiving this because you asked to hear from the center. <a href="{SITE_URL}newsletters/{ym}.html" style="color:#044978">Read this issue on the web</a> &middot;
    <a href="{SITE_URL}" style="color:#044978">smartcyberphysical.org</a> &middot; <a href="mailto:Vinod_Vokkarane@uml.edu?subject=Unsubscribe" style="color:#044978">Unsubscribe</a><br>
    Center for Smart Cyber-Physical Systems, University of Massachusetts Lowell, 1 University Ave., Lowell, MA 01854.
  </td></tr>
</table></td></tr></table></body></html>"""
    open(os.path.join(ndir, f"{ym}-email.html"), "w", encoding="utf-8").write(email)

    # ---- plain text
    txt = [f"CENTER FOR SMART CYBER-PHYSICAL SYSTEMS, UMASS LOWELL", f"Newsletter, {label}", "", lead, ""]
    if awards:
        txt.append("NEW AWARDS"); txt += [f"- {pr['title']} ({pr.get('amount','')}). {pr['sponsor']}. {pr['team']}" for pr in awards]; txt.append("")
    if papers:
        txt.append("NEW PAPERS")
        for p in papers:
            au = p["authors"] if isinstance(p["authors"], str) else ", ".join(p["authors"])
            txt.append(f"- {au}. {p['title']}. {p['venue']}, {p['details']}." + (f" https://doi.org/{p['doi']}" if p.get("doi") else ""))
        txt.append("")
    _sp = next((s for s in SPOTLIGHTS if s["ym"] == ym), None)
    if _sp: txt += ["STUDENT SPOTLIGHT", f"{_sp['title']}: {' and '.join(_sp['students'])}. {_sp['deck']} {SITE_URL}spotlight.html#{_sp['ym']}", ""]
    if notes: txt.append("MILESTONES"); txt += [f"- {t}" for t in notes]; txt.append("")
    if upcoming: txt.append("COMING UP"); txt += [f"- {pr['title']} starts {pr['period'].split(' to ')[0]}." for pr in upcoming]; txt.append("")
    txt += [f"Read on the web: {SITE_URL}newsletters/{ym}.html", f"Site: {SITE_URL}", "Unsubscribe: reply with the subject Unsubscribe."]
    open(os.path.join(ndir, f"{ym}.txt"), "w", encoding="utf-8").write("\n".join(txt) + "\n")

    build_newsletter_index(footer_html, script_html)
    print(f"wrote newsletters/{ym}.html, -email.html, .txt: {len(awards)} awards, {len(papers)} papers, {len(notes)} milestones")

def build_print_viewers(footer_html, script_html):
    """newsletters/print-<ym>.html: a page-by-page viewer for each print edition, rendered in the browser with PDF.js
    (self-hosted in vendor/pdfjs), with a two-page spread on wide screens, keyboard arrows, and a download link."""
    global FONT_ROOT
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    pdir = os.path.join(root, "newsletters", "print")
    if not os.path.isdir(pdir): return
    for f in sorted(os.listdir(pdir)):
        m = re.fullmatch(r"SCyPS-Newsletter-(\d{4}-\d{2})-Vol(\d+)-No(\d+)\.pdf", f)
        if not m: continue
        ym, vol, no = m.groups(); label = f"{MONTH_FULL[int(ym[5:7])]} {ym[:4]}"
        body = f'''<section>
  <div class="wrap">
    <p class="crumb"><a href="../news.html#newsletters">Newsletters</a></p>
    <div class="shead"><h1>{esc(label)}</h1><p>Volume {vol}, Number {no}, print edition. Read it here page by page, or download the PDF.</p></div>
    <div class="pv" id="pv" data-pdf="print/{f}">
      <div class="pvbar" role="toolbar" aria-label="Page controls">
        <button type="button" id="pvprev" aria-label="Previous page">&larr; Previous</button>
        <span class="pvpage" aria-live="polite"><span id="pvnum">1</span> of <span id="pvtot">&hellip;</span></span>
        <button type="button" id="pvnext" aria-label="Next page">Next &rarr;</button>
        <span class="pvsp"></span>
        <button type="button" id="pvspread" aria-pressed="false">Two pages</button>
        <a class="pvdl" href="print/{f}" download>Download PDF</a>
      </div>
      <div class="pvstage" id="pvstage" tabindex="0" aria-label="Newsletter pages"><p class="pvload">Loading the issue&hellip;</p></div>
      <noscript><p><a href="print/{f}">Open the PDF</a></p></noscript>
    </div>
  </div>
</section>'''
        css = '''.crumb{font-size:14px;margin-bottom:12px}
.pv{max-width:1180px}.pvbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:0 0 14px}
.pvbar button,.pvdl{font:inherit;font-size:14px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:6px 14px;cursor:pointer;text-decoration:none}
.pvbar button[aria-pressed="true"]{border-color:var(--ink);font-weight:600}.pvbar button:disabled{opacity:.4;cursor:default}
.pvpage{font-size:14px;color:var(--ink-2);min-width:70px;text-align:center}.pvsp{flex:1}
.pvstage{display:flex;justify-content:center;gap:14px;background:var(--bg-2);border:1px solid var(--line);border-radius:12px;padding:18px;outline:none;min-height:420px}
.pvstage canvas{background:#fff;box-shadow:0 2px 10px rgba(14,32,54,.18);max-width:100%;height:auto}
.pvload{color:var(--ink-3);align-self:center}
@media (max-width:760px){.pvstage{padding:8px}.pvbar .pvsp{display:none}#pvspread{display:none}}'''
        js = '''
<script src="../vendor/pdfjs/pdf.min.js"></script>
<script>
(function(){
  var box=document.getElementById('pv'), stage=document.getElementById('pvstage');
  if(!box||!window.pdfjsLib){return;}
  pdfjsLib.GlobalWorkerOptions.workerSrc='../vendor/pdfjs/pdf.worker.min.js';
  var doc=null, page=1, spread=false, busy=false;
  var num=document.getElementById('pvnum'), tot=document.getElementById('pvtot');
  var prev=document.getElementById('pvprev'), next=document.getElementById('pvnext'), sp=document.getElementById('pvspread');
  function wide(){return window.innerWidth>=900;}
  function step(){return (spread&&wide())?2:1;}
  function first(){ // in spread mode the cover stands alone, then pages pair up 2-3, 4-5, ...
    if(step()===1) return page; return page===1?1:(page%2===0?page:page-1);}
  function render(){
    if(!doc||busy) return; busy=true;
    var p0=first(), pages=[p0]; if(step()===2&&p0>1&&p0+1<=doc.numPages) pages.push(p0+1);
    var avail=stage.clientWidth-36-(pages.length-1)*14, per=avail/pages.length;
    Promise.all(pages.map(function(n){return doc.getPage(n);})).then(function(ps){
      stage.innerHTML='';
      var ratio=window.devicePixelRatio||1;
      return Promise.all(ps.map(function(pg){
        var v1=pg.getViewport({scale:1}), maxH=window.innerHeight*0.86;
        var s=Math.min(per/v1.width, maxH/v1.height), v=pg.getViewport({scale:s*ratio});
        var c=document.createElement('canvas'); c.width=v.width; c.height=v.height;
        c.style.width=(v.width/ratio)+'px'; c.style.height=(v.height/ratio)+'px';
        c.setAttribute('role','img'); c.setAttribute('aria-label','Page '+pg.pageNumber+' of '+doc.numPages);
        stage.appendChild(c);
        return pg.render({canvasContext:c.getContext('2d'),viewport:v}).promise;
      }));
    }).then(function(){
      num.textContent=pages.length>1?(pages[0]+'-'+pages[1]):pages[0];
      prev.disabled=pages[0]<=1; next.disabled=pages[pages.length-1]>=doc.numPages; busy=false;
    }).catch(function(){busy=false; stage.innerHTML='<p class="pvload">This issue could not be displayed here. <a href="'+box.dataset.pdf+'">Open the PDF</a>.</p>';});
  }
  function go(d){ if(!doc) return; var p0=first();
    if(step()===2){ page = d>0 ? (p0===1?2:p0+2) : (p0<=3?1:p0-2); } else { page=Math.min(doc.numPages,Math.max(1,page+d)); }
    page=Math.min(doc.numPages,Math.max(1,page)); render(); }
  prev.addEventListener('click',function(){go(-1);}); next.addEventListener('click',function(){go(1);});
  sp.addEventListener('click',function(){spread=!spread; sp.setAttribute('aria-pressed',String(spread)); render();});
  stage.addEventListener('keydown',function(e){if(e.key==='ArrowRight'){go(1);e.preventDefault();} if(e.key==='ArrowLeft'){go(-1);e.preventDefault();}});
  document.addEventListener('keydown',function(e){if(e.target.tagName==='INPUT')return; if(e.key==='ArrowRight')go(1); if(e.key==='ArrowLeft')go(-1);});
  var t; window.addEventListener('resize',function(){clearTimeout(t); t=setTimeout(render,200);});
  pdfjsLib.getDocument(box.dataset.pdf).promise.then(function(d){doc=d; tot.textContent=d.numPages; if(wide()){spread=true; sp.setAttribute('aria-pressed','true');} render();})
    .catch(function(){stage.innerHTML='<p class="pvload">This issue could not be loaded here. <a href="'+box.dataset.pdf+'">Open the PDF</a>.</p>';});
})();
</script>'''
        FONT_ROOT = "../"
        page = page_shell(f"{label} print edition | SCyPS, UMass Lowell",
                          f"The Center for Smart Cyber-Physical Systems newsletter, {label}, Volume {vol}, Number {no}: read the print edition page by page.",
                          body, footer_html, script_html + js, extra_css=css, active="news", canonical=f"newsletters/print-{ym}.html")
        for nm in ("index", "people", "students", "alumni", "publications", "insights", "acnl", "spotlight", "news", "labs", "summit", "positions"):
            page = page.replace(f'href="{nm}.html', f'href="../{nm}.html')
        page = re.sub(r'href="research-(\w+)\.html', r'href="../research-\1.html', page)
        page = page.replace('href="../index.html">Newsletters', 'href="index.html">Newsletters')
        open(os.path.join(root, "newsletters", f"print-{ym}.html"), "w", encoding="utf-8").write(new_tab_links(page))
        FONT_ROOT = ""
        print(f"wrote newsletters/print-{ym}.html (viewer for {f})")

def build_newsletter_index(footer_html, script_html):
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    ndir = os.path.join(root, "newsletters"); os.makedirs(ndir, exist_ok=True)
    issues = sorted([f[:7] for f in os.listdir(ndir) if re.fullmatch(r"\d{4}-\d{2}\.html", f)], reverse=True)
    rows = "".join(f'<li><a href="{ym}.html">{MONTH_FULL[int(ym[5:7])]} {ym[:4]}</a></li>' for ym in issues)
    # Print editions: designed PDF issues made with print_newsletter.py, listed newest first with their covers
    pdir = os.path.join(ndir, "print"); prints = []
    for f in sorted(os.listdir(pdir), reverse=True) if os.path.isdir(pdir) else []:
        m = re.fullmatch(r"SCyPS-Newsletter-(\d{4}-\d{2})-Vol(\d+)-No(\d+)\.pdf", f)
        if not m: continue
        pym, vol, no = m.groups(); cover = f"print/{pym}-cover.jpg"
        cov = f'<img src="{cover}" alt="" width="240" height="311">' if os.path.exists(os.path.join(pdir, f"{pym}-cover.jpg")) else ""
        prints.append(f'<li><a href="print-{pym}.html">{cov}<span><b>Volume {vol}, Number {no}</b>{MONTH_FULL[int(pym[5:7])]} {pym[:4]} print edition<em>Read online</em></span></a><a class="prdl" href="print/{f}" download>Download PDF</a></li>')
    print_html = (f'<h2 class="grouph">Print editions</h2><ul class="prlist">{"".join(prints)}</ul>') if prints else ""
    body = f"""<section>
  <div class="wrap">
    <div class="shead"><h1>Newsletters</h1><p>The center's monthly note, one issue per month, generated from its own records of papers, awards, and milestones. Each issue is also available as an email and as plain text. Print editions carry the month's spotlights on a student, a faculty member, and a project.</p></div>
    {print_html}
    <h2 class="grouph">Monthly issues</h2>
    <ul class="nllist">{rows or "<li>No issues yet.</li>"}</ul>
    <p class="nlfoot">Prefer items as they happen? Subscribe to the <a href="../feed.xml">news feed</a>.</p>
  </div>
</section>"""
    css = ".prlist{list-style:none;margin:0 0 30px;padding:0;display:flex;flex-wrap:wrap;gap:20px}.prlist a{display:flex;gap:16px;align-items:flex-start;border:1px solid var(--line);border-radius:10px;padding:12px;background:var(--surface);color:var(--ink);text-decoration:none;max-width:420px}.prlist img{width:120px;height:auto;border:1px solid var(--line);border-radius:4px}.prlist span{font-size:15px;line-height:1.4}.prlist b{display:block;font-size:17px;margin-bottom:4px}.prlist em{display:block;font-style:normal;color:var(--accent,#044978);margin-top:8px;font-weight:600}.prlist li{display:flex;flex-direction:column;gap:6px}.prdl{font-size:14px;padding-left:4px}" + ".nllist{list-style:none;margin:0;padding:0;max-width:30em}.nllist li{padding:12px 0;border-bottom:1px solid var(--line);font-size:17px}.nlfoot{font-size:13.5px;color:var(--ink-3);margin-top:30px}"
    global FONT_ROOT
    FONT_ROOT = "../"
    page = page_shell("Newsletters | SCyPS, UMass Lowell", "Monthly newsletters from the Center for Smart Cyber-Physical Systems at UMass Lowell.",
                      body, footer_html, script_html, extra_css=css, active="news", canonical="newsletters/index.html")
    for nm in ("index", "people", "students", "alumni", "publications", "insights", "news", "labs", "summit", "positions"):
        page = page.replace(f'href="{nm}.html', f'href="../{nm}.html')
    page = re.sub(r'href="research-(\w+)\.html', r'href="../research-\1.html', page)
    page = page.replace('href="../index.html#', 'href="../index.html#')
    open(os.path.join(ndir, "index.html"), "w", encoding="utf-8").write(
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Newsletters | SCyPS</title>'
        '<meta http-equiv="refresh" content="0; url=../news.html#newsletters"><link rel="canonical" href="https://smartcyberphysical.org/news.html">'
        '</head><body><p>The newsletters now live on the <a href="../news.html#newsletters">News page</a>.</p></body></html>')
    FONT_ROOT = ""

def load_portraits():
    """Alumni portraits dropped into portraits/ beside the build script, keyed alum_<slug>."""
    import base64
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portraits")
    if not os.path.isdir(d): return
    for f in os.listdir(d):
        if f.lower().endswith((".jpg", ".jpeg")):
            IMG["alum_" + os.path.splitext(f)[0].lower()] = base64.b64encode(open(os.path.join(d, f), "rb").read()).decode()
load_portraits()

def build_assets():
    """Files other services fetch by URL: the logo for the email header and the social card. Also the
    self-hosted fonts, copied from fonts/ beside build_site.py."""
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    import shutil
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    dst = os.path.join(root, "fonts")
    # In the repository the site is built in place, so source and destination are the same folder
    # and there is nothing to copy. Only copy when building into a separate output folder.
    if os.path.isdir(src) and os.path.realpath(src) != os.path.realpath(dst):
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src):
            if f.endswith(".woff2"): shutil.copy(os.path.join(src, f), os.path.join(dst, f))
    import base64
    open(os.path.join(root, "logo-mark.png"), "wb").write(base64.b64decode(IMG["logo_mark"]))
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        card = Image.new("RGB", (1200, 630), (4, 73, 120))
        mark = Image.open(io.BytesIO(base64.b64decode(IMG["logo_full"]))).convert("RGBA")
        mark.thumbnail((520, 330))
        panel = Image.new("RGB", (mark.width + 60, mark.height + 60), (255, 255, 255))
        card.paste(panel, (80, 315 - panel.height // 2)); card.paste(mark, (110, 315 - mark.height // 2), mark)
        d = ImageDraw.Draw(card)
        try:
            fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
            fr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        except Exception:
            fb = fr = None
        x = 80 + panel.width + 50
        d.text((x, 235), "Center for Smart", font=fb, fill=(255, 255, 255))
        d.text((x, 290), "Cyber-Physical Systems", font=fb, fill=(255, 255, 255))
        d.text((x, 360), "University of Massachusetts Lowell", font=fr, fill=(201, 220, 234))
        d.text((x, 400), "smartcyberphysical.org", font=fr, fill=(159, 220, 214))
        card.save(os.path.join(root, "og-card.png"), optimize=True)
    except Exception as e:
        print("og-card.png not written:", e)
    print("wrote logo-mark.png and og-card.png")

def build_meta_files():
    """robots.txt and sitemap.xml, so the new pages are discoverable and the old single page is not the only entry."""
    root = os.path.dirname(os.path.abspath(OUT)) or "."
    pages = ["", "people.html", "students.html", "alumni.html", "publications.html", "insights.html", "acnl.html", "spotlight.html",
             "acnl/index.html", "acnl/research.html", "acnl/insights.html", "acnl/people.html", "acnl/publications.html", "acnl/projects.html", "acnl/software.html", "acnl/join.html"] + \
            [f"acnl/students/{re.sub(r'[^a-z]+', '-', s['name'].lower()).strip('-')}.html" for s in STUDENTS if s.get("advisor") == FACULTY["director"]["name"]] + \
            [f"acnl/projects/{f}" for f in (sorted(os.listdir(os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "acnl", "projects"))) if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "acnl", "projects")) else []) if f.endswith(".html")] + [ "news.html", "summit.html", "labs.html", "positions.html"] + \
            [f"research-{k}.html" for k, _, _, _ in THRUSTS]
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in pages)
    open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    open(os.path.join(root, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
    print(f"wrote sitemap.xml ({len(pages)} urls) and robots.txt")

def build_insights(footer_html, script_html):
    """insights.html: the records read together (clusters, collaboration, citations, students, alumni,
    projects). The computation lives in insights.py beside this file; graph_auto.json holds the Crossref
    reference lists and citation counts that graph_fetch.py refreshes weekly."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            import networkx
        except ImportError:          # the GitHub runner starts bare; install the one dependency
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "networkx"], check=False)
        import insights
        insights.render(globals(), footer_html, script_html)
    except Exception as e:
        print(f"insights.html skipped: {e}")

def _person_key(n):
    p = re.sub(r"\(.*?\)", "", n).replace(".", " ").split()
    return (p[-1].lower() + "_" + p[0][0].lower()) if p else ""

def _college_of(p):
    """Where a person sits: a UMass Lowell college for internal people, the institution for external ones."""
    t = (p.get("title", "") + " " + p.get("title2", "")).lower(); inst = p.get("inst", "") or ""
    if inst or "nyu" in t or "external" in (p.get("tag") or "").lower():
        known = {"West Virginia": "West Virginia University", "NYU": "NYU Tandon", "New York University": "NYU Tandon", "Louisiana": "University of Louisiana at Lafayette"}
        if inst: return known.get(inst, inst)
        if "nyu" in t: return "NYU Tandon"
        return p.get("title", "").split(",")[-1].strip() or "External"      # "Research Director of the Northeast US, Red Hat"
    if any(k in t for k in ("electrical", "civil", "chemical", "nuclear", "mechanical", "plastics", "engineering")): return "Francis College of Engineering"
    if any(k in t for k in ("computer science", "physics", "miner school")): return "Kennedy College of Sciences"
    if any(k in t for k in ("philosophy", "school of education", "fine arts")): return "College of Fine Arts, Humanities and Social Sciences"
    return "UMass Lowell"

def _thumb(key, px=96):
    """A small JPEG of a portrait for the graph, so the page does not carry the full-size photo twice."""
    import base64, io
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(IMG[key]))).convert("RGB").resize((px, px), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=78, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def center_on(sub, hub, pos, x0, y0, w, h):
    """Radial layout with the hub person in the middle of the box: direct collaborators on the first ring,
    their collaborators on the next, and so on. The order around each ring follows a Kamada-Kawai layout so
    groups that work together stay together; outer people sit near the people who connect them inward."""
    import networkx as nx, math
    dist = nx.single_source_shortest_path_length(sub, hub)
    K = max(dist.values()) or 1
    kk = nx.kamada_kawai_layout(sub, weight=None); hx, hy = kk[hub]
    ang = {n: math.atan2(kk[n][1] - hy, kk[n][0] - hx) for n in sub if n != hub}
    cx, cy = x0 + w / 2, y0 + h / 2
    placed = {hub: 0.0}
    for ring in range(1, K + 1):
        members = [n for n, d in dist.items() if d == ring]
        if ring > 1:   # pull each outer person toward the mean angle of their inner-ring neighbors
            for n in members:
                inner = [placed[m] for m in sub[n] if m in placed and dist[m] == ring - 1]
                if inner: ang[n] = math.atan2(sum(math.sin(a) for a in inner), sum(math.cos(a) for a in inner))
        members.sort(key=lambda n: ang[n])
        m = len(members); gap = 2 * math.pi / max(m, 1)
        if ring == 1:   # spread the first ring evenly, keeping its order
            start = ang[members[0]] if members else 0
            for k, n in enumerate(members): placed[n] = start + k * gap
        else:           # keep outer people near their anchors but at least a minimum angle apart
            mind = min(gap, math.radians(28))
            for k, n in enumerate(members):
                a = ang[n]
                if k and a - placed[members[k - 1]] < mind: a = placed[members[k - 1]] + mind
                placed[n] = a
        f = 0.9 if K == 1 else 0.52 + 0.48 * (ring - 1) / (K - 1)     # first ring at about half the radius
        rx, ry = (w / 2) * f, (h / 2) * f
        for n in members: pos[n] = (cx + rx * math.cos(placed[n]), cy + ry * math.sin(placed[n]))
    pos[hub] = (cx, cy)

def collab_graph_html():
    """Who works with whom among the faculty and external collaborators: a link for every co-authored paper in the
    center record and every shared award. Each person is drawn with their photo, ringed in the color of their
    college or institution. Laid out per connected component; people with no joint work yet are listed below."""
    try: import networkx as nx
    except ImportError: return ""
    people = [FACULTY["director"]] + FACULTY["core"] + FACULTY["affiliated"] + FACULTY["external"]
    nodes = {_person_key(p["name"]): {"name": re.sub(r"\s*\(.*?\)", "", p["name"]), "where": _college_of(p), "photo": p.get("photo") or ""} for p in people}
    G = nx.Graph(); G.add_nodes_from(nodes)
    def link(a, b, kind):
        if a == b or a not in nodes or b not in nodes: return
        if G.has_edge(a, b): G[a][b]["w"] += 1; G[a][b][kind] += 1
        else: G.add_edge(a, b, w=1, paper=0, award=0); G[a][b][kind] += 1
    for p in P:
        ks = sorted({k for k in {_person_key(a) for a in p["authors"]} if k in nodes})
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)): link(ks[i], ks[j], "paper")
    for pr in PROJECTS:
        team = pr.get("team", ""); words = set(re.findall(r"[A-Za-z][A-Za-z-]+", team))
        ks = sorted(k for k, d in nodes.items() if d["name"] in team or d["name"].split()[-1] in words)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)): link(ks[i], ks[j], "award")
    by_sur = {d["name"].split()[-1]: k for k, d in nodes.items()}
    groups = {}
    for key, title, _, who in THRUSTS:
        listed = {by_sur[s.strip()] for s in who.split(",") if s.strip() in by_sur}
        g = set(listed)
        for pr in PROJECTS:     # only awards in this thrust that one of its listed faculty is on
            if project_thrust(pr) != key: continue
            team = pr.get("team", ""); words = set(re.findall(r"[A-Za-z][A-Za-z-]+", team))
            named = {k for k, d in nodes.items() if d["name"] in team or d["name"].split()[-1] in words}
            if named & listed: g |= named
        groups[key] = g
    alone = sorted(nodes[n]["name"] for n in G if G.degree(n) == 0)
    G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
    if not len(G): return ""
    W, H, M = 1100, 760, 70
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    pos = {}
    def fit(sub, x0, y0, w, h):
        p = nx.kamada_kawai_layout(sub, weight=None) if len(sub) > 2 else nx.circular_layout(sub)
        xs = [v[0] for v in p.values()]; ys = [v[1] for v in p.values()]
        for n, (x, y) in p.items():
            pos[n] = (x0 + (x - min(xs)) / (max(xs) - min(xs) or 1) * w, y0 + (y - min(ys)) / (max(ys) - min(ys) or 1) * h)
    side = 170 if len(comps) > 1 else 0
    hub = _person_key(FACULTY["director"]["name"])
    if hub in comps[0]:
        center_on(G.subgraph(comps[0]), hub, pos, M + side, M, W - 2 * M - side, H - 2 * M - 10)
    else:
        fit(G.subgraph(comps[0]), M + side, M, W - 2 * M - side, H - 2 * M - 10)
    cy = M
    for c in comps[1:]:
        fit(G.subgraph(c), M, cy, 110, 70); cy += 150
    # Nudge apart any two people whose photo-and-name boxes would overlap (each box is about 150 x 84 px),
    # moving along whichever axis needs the smaller push, and keep everyone on the canvas.
    BW, BH = 150, 84
    for _ in range(400):
        moved = False; ks = list(pos)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                (x1, y1), (x2, y2) = pos[ks[i]], pos[ks[j]]
                ox, oy = BW - abs(x1 - x2), BH - abs(y1 - y2)
                if ox > 0 and oy > 0:
                    moved = True
                    fi, fj = (0 if ks[i] == hub else 1), (0 if ks[j] == hub else 1)   # the director stays put
                    k2 = 2 / (fi + fj)
                    if ox < oy:
                        s = (ox / 2 + 1) * (1 if x1 >= x2 else -1) * k2; pos[ks[i]] = (x1 + s * fi, y1); pos[ks[j]] = (x2 - s * fj, y2)
                    else:
                        s = (oy / 2 + 1) * (1 if y1 >= y2 else -1) * k2; pos[ks[i]] = (x1, y1 + s * fi); pos[ks[j]] = (x2, y2 - s * fj)
        for n, (x, y) in pos.items(): pos[n] = (min(W - M, max(M, x)), min(H - M - 12, max(M - 10, y)))
        if not moved: break
    order = ["Francis College of Engineering", "Kennedy College of Sciences", "College of Fine Arts, Humanities and Social Sciences", "UMass Lowell"]
    order += sorted({nodes[n]["where"] for n in G} - set(order))
    palette = ["#044978", "#2CA58D", "#C2185B", "#8A8F98", "#D4A017", "#8E5BB2", "#E4572E", "#3F8FD2", "#5B8C5A"]
    color = {w: palette[i % len(palette)] for i, w in enumerate(order)}
    maxw = max(d["w"] for _, _, d in G.edges(data=True))
    edges = []
    for a, b, d in sorted(G.edges(data=True), key=lambda e: e[2]["w"]):
        t = f"{nodes[a]['name']} and {nodes[b]['name']}: {d['paper']} joint paper{'s' if d['paper'] != 1 else ''}" + (f", {d['award']} shared award{'s' if d['award'] != 1 else ''}" if d["award"] else "")
        op = 0.25 + 0.55 * (d["w"] / maxw) ** 0.5
        et = " ".join(k for k, g in groups.items() if a in g and b in g)
        edges.append(f'<line data-t="{et}" data-a="{a}" data-b="{b}" data-info="{esc(t)}" x1="{pos[a][0]:.0f}" y1="{pos[a][1]:.0f}" x2="{pos[b][0]:.0f}" y2="{pos[b][1]:.0f}" stroke-width="{1.2 + 7 * (d["w"] / maxw) ** 0.6:.1f}" stroke-opacity="{op:.2f}"/>')
    defs, dots = [], []
    for n in G:
        d = nodes[n]; deg = G.degree(n, weight="w"); r = 20 + min(14, deg ** 0.5 * 1.6); x, y = pos[n]
        tip = f'{d["name"]}, {d["where"]}: {G.degree(n)} collaborator{"s" if G.degree(n) != 1 else ""} in the center, {deg} joint papers and awards'
        if d["photo"] and IMG.get("head_" + d["photo"]):
            cid = "cc_" + n.replace("_", "")
            defs.append(f'<clipPath id="{cid}"><circle cx="{x:.0f}" cy="{y:.0f}" r="{r - 3:.1f}"/></clipPath>')
            face = f'<image href="{_thumb("head_" + d["photo"])}" x="{x - r + 3:.0f}" y="{y - r + 3:.0f}" width="{2 * r - 6:.0f}" height="{2 * r - 6:.0f}" clip-path="url(#{cid})" preserveAspectRatio="xMidYMid slice"/>'
        else:
            ini = "".join(w[0] for w in d["name"].split() if w[0].isupper())[:2]
            face = f'<text x="{x:.0f}" y="{y + 5:.0f}" text-anchor="middle" class="ini">{esc(ini)}</text>'
        nt = " ".join(k for k, g in groups.items() if n in g)
        nbrs = sorted(G[n], key=lambda m: -G[n][m]["w"])
        def _cnt(x, word): return f"{x} {word}{'s' if x != 1 else ''}"
        who = "|".join(f'{nodes[m]["name"]}: ' + ", ".join(v for v in (_cnt(G[n][m]["paper"], "paper") if G[n][m]["paper"] else "", _cnt(G[n][m]["award"], "award") if G[n][m]["award"] else "") if v) for m in nbrs)
        dots.append(f'<g class="cn" data-t="{nt}" data-k="{n}" data-name="{esc(d["name"])}" data-where="{esc(d["where"])}" data-who="{esc(who)}" tabindex="0" role="button" aria-label="{esc(tip)}"><circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff" stroke="{color[d["where"]]}" stroke-width="4"/>{face}'
                    f'<text x="{x:.0f}" y="{y + r + 16:.0f}" text-anchor="middle" class="nm">{esc(d["name"])}</text></g>')
    legend = "".join(f'<span class="lg"><i style="border-color:{color[w]}"></i>{esc(w)}</span>' for w in order if any(nodes[n]["where"] == w for n in G))
    alone_html = (f'<p class="collabnote">No joint paper or award with another member in the record yet: {esc(", ".join(alone))}.</p>' if alone else "")
    return f'''<section id="collab">
  <div class="wrap">
    <div class="shead"><h2>Who works with whom</h2><p>The center's faculty and collaborators, linked by every co-authored paper in the center record and every shared award. Each ring shows the person's college or institution; thicker lines mean more joint work. Hover over a person to see who they work with, or over a line to see what they did together.</p></div>
    <div class="legend">{legend}</div>
    <div class="cfilters" role="group" aria-label="Show a thrust"><span class="flab">Thrust</span><button class="chip" data-ct="all" aria-pressed="true" type="button">Everyone</button>{"".join(f'<button class="chip" data-ct="{esc(k)}" aria-pressed="false" type="button">{esc(t.split(" and ")[0].split(",")[0])} ({len([n for n in groups[k] if n in G])})</button>' for k, t, _, _ in THRUSTS if len([n for n in groups[k] if n in G]) > 1)}</div>
    <p class="cnote" id="cnote" aria-live="polite"></p>
    <div class="collabwrap" id="collabwrap"><div class="ctip" id="ctip" role="status" hidden></div><svg class="collab" viewBox="0 0 {W} {H}" role="img" aria-label="Collaboration graph of center faculty and collaborators">
      <defs>{"".join(defs)}</defs><g class="ce">{"".join(edges)}</g>{"".join(dots)}
    </svg></div>{alone_html}
  </div>
</section>
<script>
(function(){{
  var svg=document.querySelector('svg.collab'); if(!svg) return;
  var tip=document.getElementById('ctip'), wrap=document.getElementById('collabwrap');
  function place(e){{var r=wrap.getBoundingClientRect(); var x=e.clientX-r.left+wrap.scrollLeft+14, y=e.clientY-r.top+14;
    if(x+320>wrap.scrollLeft+r.width) x=x-340; tip.style.left=x+'px'; tip.style.top=y+'px';}}
  function clear(){{svg.classList.remove('hover'); svg.querySelectorAll('.hl').forEach(function(el){{el.classList.remove('hl');}}); tip.hidden=true;}}
  function person(g,e){{
    clear(); var k=g.getAttribute('data-k'); svg.classList.add('hover'); g.classList.add('hl'); var n=0, p=0;
    svg.querySelectorAll('.ce line').forEach(function(l){{
      var a=l.getAttribute('data-a'), b=l.getAttribute('data-b');
      if(a===k||b===k){{ l.classList.add('hl'); n++; var o=svg.querySelector('.cn[data-k="'+(a===k?b:a)+'"]'); if(o) o.classList.add('hl'); }}
    }});
    var who=g.getAttribute('data-who').split('|');
    tip.innerHTML='<b>'+g.getAttribute('data-name')+'</b><span class="cw">'+g.getAttribute('data-where')+'</span><span class="cn2">'+n+' collaborator'+(n===1?'':'s')+' in the center</span><ul>'+who.slice(0,8).map(function(s){{return '<li>'+s+'</li>';}}).join('')+(who.length>8?'<li>and '+(who.length-8)+' more</li>':'')+'</ul>';
    tip.hidden=false; if(e) place(e);
  }}
  function link(l,e){{
    clear(); svg.classList.add('hover'); l.classList.add('hl');
    [l.getAttribute('data-a'),l.getAttribute('data-b')].forEach(function(k){{var o=svg.querySelector('.cn[data-k="'+k+'"]'); if(o) o.classList.add('hl');}});
    tip.innerHTML='<b>'+l.getAttribute('data-info').replace(': ','</b><span class="cn2">')+'</span>'; tip.hidden=false; place(e);
  }}
  svg.querySelectorAll('.cn').forEach(function(g){{
    g.addEventListener('mouseenter',function(e){{person(g,e);}}); g.addEventListener('mousemove',place); g.addEventListener('mouseleave',clear);
    g.addEventListener('focus',function(){{person(g,null); var r=g.getBoundingClientRect(), w=wrap.getBoundingClientRect(); tip.style.left=(r.right-w.left+wrap.scrollLeft+8)+'px'; tip.style.top=(r.top-w.top)+'px';}});
    g.addEventListener('blur',clear);
    g.addEventListener('click',function(e){{ e.stopPropagation(); person(g,e); }});   // taps on phones
  }});
  svg.querySelectorAll('.ce line').forEach(function(l){{
    l.addEventListener('mouseenter',function(e){{link(l,e);}}); l.addEventListener('mousemove',place); l.addEventListener('mouseleave',clear);
  }});
  document.addEventListener('click',function(e){{ if(!e.target.closest('svg.collab .cn')) clear(); }});
  var names={{{",".join(f'"{k}":"{esc(t)}"' for k, t, _, _ in THRUSTS)}}};
  var note=document.getElementById('cnote');
  document.querySelectorAll('.cfilters .chip').forEach(function(b){{
    b.addEventListener('click',function(){{
      document.querySelectorAll('.cfilters .chip').forEach(function(x){{x.setAttribute('aria-pressed','false');}});
      b.setAttribute('aria-pressed','true');
      var k=b.getAttribute('data-ct');
      svg.classList.toggle('focus',k!=='all');
      var n=0;
      svg.querySelectorAll('[data-t]').forEach(function(el){{
        var on=k!=='all' && (' '+el.getAttribute('data-t')+' ').indexOf(' '+k+' ')>=0;
        el.classList.toggle('on',on); if(on && el.tagName==='g') n++;
      }});
      note.textContent = k==='all' ? '' : names[k]+': '+n+' people, their joint papers and shared awards highlighted.';
    }});
  }});
}})();
</script>'''

COLLAB_CSS = (".collabwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface)}"
              ".collab{width:100%;min-width:760px;height:auto;display:block}.collab .ce line{stroke:var(--ink-3)}"
              ".collab .nm{font-size:14px;font-weight:600;fill:var(--ink);font-family:'IBM Plex Sans',sans-serif;paint-order:stroke;stroke:var(--surface);stroke-width:4px;stroke-linejoin:round}"
              ".collab .ini{font-size:15px;font-weight:600;fill:var(--ink-2);font-family:'IBM Plex Sans',sans-serif}"
              ".collab .cn:hover circle{stroke-width:6}.collab .ce line:hover{stroke:var(--ink);stroke-opacity:.9}"
              ".legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 12px;font-size:14px;color:var(--ink-2)}.lg{display:inline-flex;align-items:center;gap:7px}"
              ".lg i{width:13px;height:13px;border-radius:50%;display:inline-block;border:3px solid;background:#fff}"
              ".collabnote{font-size:14px;color:var(--ink-3);margin:10px 0 0;max-width:60em}"
              ".cfilters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 8px}.cfilters .flab{font-size:13px;color:var(--ink-3);margin-right:4px}"
              ".cfilters .chip{font:inherit;font-size:13.5px;padding:5px 12px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);border-radius:999px;cursor:pointer}"
              ".cfilters .chip[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}.cnote{font-size:14px;color:var(--ink-2);min-height:1.4em;margin:0 0 8px}"
              ".collabwrap{position:relative}.ctip{position:absolute;z-index:3;max-width:320px;background:var(--surface);border:1px solid var(--line);border-radius:10px;box-shadow:0 8px 24px rgba(14,32,54,.16);padding:10px 12px;font-size:13.5px;line-height:1.4;color:var(--ink-2);pointer-events:none}"
              ".ctip b{display:block;font-size:15px;color:var(--ink)}.ctip .cw{display:block;color:var(--ink-3);font-size:12.5px;margin:1px 0 4px}.ctip .cn2{display:block;font-weight:600;color:var(--ink);margin:2px 0}"
              ".ctip ul{margin:4px 0 0;padding-left:16px}.ctip li{margin:0 0 1px}.collab .cn{cursor:pointer;outline:none}.collab .ce line{cursor:pointer}"
              ".collab.hover .cn:not(.hl){opacity:.14}.collab.hover .ce line{stroke-opacity:.04!important}.collab.hover .ce line.hl{stroke-opacity:.9!important;stroke:var(--signal)}"
              ".collab .cn,.collab .ce line{transition:opacity .2s,stroke-opacity .2s}.collab.focus .cn:not(.on){opacity:.15}"
              ".collab.focus .ce line{stroke-opacity:.05!important}.collab.focus .ce line.on{stroke-opacity:.85!important;stroke:var(--signal)}")


def build_acnl(footer_html, script_html):
    """acnl.html: the lab's full paper record, 2002 to 2026 (acnl_insights.py, acnl_records.json)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import acnl_insights
        acnl_insights.render(globals(), footer_html, script_html)
    except Exception as e:
        print(f"acnl.html skipped: {e}")

def build_thrust_pages(footer_html, script_html):
    """One page per research thrust, sharing the site shell."""
    people_by_surname = {}
    for grp in ("director", "core", "affiliated", "external"):
        for p in ([FACULTY[grp]] if grp == "director" else FACULTY[grp]):
            people_by_surname[re.sub(r"\(.*?\)", "", p["name"]).split()[-1]] = p
    for k, title, blurb, who in THRUSTS:
        d = THRUST_DETAIL.get(k, {})
        out = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", f"research-{k}.html")
        # the faculty on this thrust
        cards = ""
        for sur in [w.strip() for w in who.split(",")]:
            p = people_by_surname.get(sur)
            if not p: continue
            cards += (f'<a class="tperson" href="people.html">{avatar(p, "sm")}<span><b>{esc(p["name"])}</b>'
                      f'<small>{esc(p.get("title", "").split(";")[0])}</small></span></a>')
        # what the group builds
        work = "".join(f'<div class="wcard"><h3>{esc(t)}</h3><p>{esc(b)}</p></div>' for t, b in d.get("work", []))
        # papers tagged to the faculty on this thrust, newest first
        tags = {w.strip() for w in who.split(",")}
        papers = [p for p in P if tags & set(p["faculty"])]
        papers.sort(key=lambda p: (-p["year"], -(month_of(p) or 0)))
        plist = "".join(
            f'<li class="pub"><div><div class="a">{fmt_authors(p["authors"])}</div>'
            f'<div class="t">{("<a href=" + chr(34) + "https://doi.org/" + esc(p["doi"]) + chr(34) + ">" + esc(p["title"]) + "</a>") if p.get("doi") else esc(p["title"])}</div>'
            f'<div class="v"><i>{esc(p["venue"])}</i>, {esc(p["details"])}{journal_chip(p["venue"]) if p["type"] == "journal" else ""}</div></div></li>' for p in papers[:8])
        # projects whose title matches one of the thrust's keys
        names = d.get("projects", [])
        projs = [pr for pr in PROJECTS if any(n.lower() in pr["title"].lower() or n.lower() in pr["sponsor"].lower() for n in names)]
        seen, uniq = set(), []
        for pr in projs:
            if pr["title"] in seen: continue
            seen.add(pr["title"]); uniq.append(pr)
        prows = "".join(
            f'<li class="tproj"><div><b>{esc(pr["title"])}</b><span class="sub">{esc(pr["sponsor"])}'
            f'{(" &middot; " + esc(pr["amount"])) if pr.get("amount") else ""}'
            f'{(" &middot; " + esc(pr["period"])) if pr.get("period") else ""}</span></div>'
            f'<span class="pill">{esc(pr["tag"])}</span></li>' for pr in uniq[:6])
        tools = "".join(
            f'<p class="tooll"><a href="{esc(u)}">{esc(n)}</a> <span class="sub">{esc(w)}</span></p>'
            for n, u, w in d.get("tools", []))
        others = "".join(
            f'<a class="othr" href="research-{esc(k2)}.html">{esc(t2)}</a>'
            for k2, t2, _, _ in THRUSTS if k2 != k)
        body = f"""<div class="thero">
  <div class="wrap">
    <p class="crumb"><a href="index.html#research">Research thrusts</a></p>
    <h1>{esc(title)}</h1>
    <p class="q">{esc(d.get("question", blurb))}</p>
  </div>
</div>
<div class="wrap"><figure class="theroart">{HERO_ART.get(k, ART[k])}</figure></div>
<section>
  <div class="wrap">
    <div class="tgrid">
      <div>
        <p class="lede">{esc(d.get("lede", blurb))}</p>
        <h2 class="grouph vh">What the group builds</h2>
        <div class="wgrid">{work}</div>
      </div>
      <aside class="tside">
        <h2 class="sideh">Faculty</h2>
        <div class="tpeople">{cards}</div>
        {("<h2 class=\"sideh\">Projects</h2><ul class=" + chr(34) + "tprojs" + chr(34) + ">" + prows + "</ul>") if prows else ""}
        {("<h2 class=\"sideh\">Tools</h2>" + tools) if tools else ""}
      </aside>
    </div>
  </div>
</section>
<section class="tint">
  <div class="wrap">
    <div class="shead"><h2>Recent papers</h2><p>The newest work from the faculty on this thrust. {len(papers)} papers since 2019 carry one of their names.</p></div>
    <ol class="publist">{plist}</ol>
    <p class="more"><a class="btn-gift summit-btn" href="publications.html">All publications</a></p>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="shead"><h2>Other thrusts</h2><p>Most projects cut across two or three of them.</p></div>
    <div class="others">{others}</div>
  </div>
</section>"""
        css = """.thero{background:var(--navy);color:#fff;padding:clamp(44px,6vw,76px) 0 clamp(80px,9vw,120px)}
.thero .crumb{font-size:14px;margin-bottom:14px}
.thero .crumb a{color:#9FC4DF}
.thero h1{color:#fff;font-size:clamp(32px,4.2vw,52px);max-width:16em}
.thero .q{font-size:clamp(17px,1.5vw,21px);color:#D6DEE8;max-width:40em;margin-top:18px}
.theroart{margin:-70px 0 0;background:#FFFFFF;border:1px solid var(--line);border-radius:var(--radius);padding:14px;position:relative;z-index:2;box-shadow:0 22px 60px -34px var(--shadow)}
.theroart svg{width:100%;height:auto;display:block}\n.theroart{--bg-2:#F3F7FA;--surface:#FFFFFF;--line:#D5DCE5;--ink:#0E2036;--ink-3:#5B6B82;--signal:#0A777F;--brand-blue:#044978;--green:#3BA995}
.tgrid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,.75fr);gap:clamp(28px,5vw,64px);align-items:start}
.lede{font-size:clamp(17px,1.4vw,19px);color:var(--ink-2);margin-bottom:30px}
.wgrid{display:grid;gap:18px}
.wcard{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--signal);border-radius:0 var(--radius) var(--radius) 0;padding:20px 22px}
.wcard h3{font-size:18px;margin-bottom:6px}
.wcard p{font-size:15px;color:var(--ink-2);margin:0}
.tside .sideh{font-size:17px;margin:0 0 12px;font-family:"Fraunces",Georgia,serif;font-weight:600}
.tside .sideh+*{margin-top:0}
.tside>.sideh~.sideh{margin-top:28px}
.tpeople{display:grid;gap:10px}
.tperson{display:flex;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:10px 12px;color:var(--ink)}
.tperson:hover{text-decoration:none;border-color:var(--ink-3)}
.tperson .avatar{width:52px;height:52px;border-radius:8px;flex:none}
.tperson b{display:block;font-size:14.5px}
.tperson small{display:block;font-size:12px;color:var(--ink-3);line-height:1.3}
.tprojs{list-style:none;margin:0;padding:0}
.tproj{display:flex;gap:10px;justify-content:space-between;align-items:flex-start;padding:11px 0;border-bottom:1px solid var(--line);font-size:14px}
.tproj .sub{display:block;color:var(--ink-3);font-size:12.5px;margin-top:2px}
.tproj .pill{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--bg-2);color:var(--ink-2);white-space:nowrap}
.tooll{font-size:14px;margin-bottom:8px}
.tooll .sub{color:var(--ink-3);font-size:12.5px;display:block}
.others{display:flex;flex-wrap:wrap;gap:10px}
.othr{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:10px 18px;font-size:14.5px;color:var(--ink)}
.othr:hover{text-decoration:none;border-color:var(--ink-3)}
@media (max-width:900px){.tgrid{grid-template-columns:1fr}.theroart{margin-top:-50px}}
.theroart .s-ink{stroke:var(--ink)}
.theroart .f-ink{fill:var(--ink)}
.theroart .f-surface{fill:var(--surface)}
.theroart .f-muted{fill:var(--ink-3)}
.theroart .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}
:root[data-theme="dark"] .theroart .card{filter:drop-shadow(0 4px 10px rgba(0,0,0,.4))}
.theroart .f-alert{fill:#E25555}
.theroart .s-alert{stroke:#E25555}
.theroart .f-alert-tint{fill:#FDECEC}
:root[data-theme="dark"] .theroart .f-alert-tint{fill:#3A1E20}
.theroart .s-sig{stroke:var(--signal)}
.theroart .f-sig{fill:var(--signal)}
.theroart .f-brand{fill:var(--brand-blue)}
.theroart .s-brand{stroke:var(--brand-blue)}
.theroart .f-grn{fill:var(--green)}
.theroart .s-grn{stroke:var(--green)}
.theroart .f-tint{fill:var(--bg-2)}
.theroart .s-line{stroke:var(--line)}
.theroart .f-line{fill:var(--line)}
.theroart .f-sigt{fill:var(--signal-tint)}
.theroart .f-amb{fill:var(--amber)}
.theroart .s-amb{stroke:var(--amber)}
.theroart .s-muted{stroke:var(--ink-3)}"""
        page = page_shell(f"{title} | SCyPS, UMass Lowell", blurb, body, footer_html, script_html, extra_css=css, active="research", canonical=f"research-{k}.html")
        page = new_tab_links(page)
        open(out, "w", encoding="utf-8").write(page)
        print(f"wrote {out}: {len(page)/1024:.0f} KB")


def build_summit(footer_html, script_html):
    """Stand-alone project page for the NSF MRI SUMMIT testbed, written next to the main page."""
    out = os.path.join(os.path.dirname(os.path.abspath(OUT)) or ".", "summit.html")
    core = {p["name"]: p for p in [FACULTY["director"]] + FACULTY["core"] + FACULTY["affiliated"] + FACULTY["external"]}
    def person(name, role):
        p = core[name]
        return f'<div class="tm">{avatar(p, "lg")}<b>{esc(name)}</b><span>{esc(role)}</span><small>{esc(p.get("title", "").split(";")[0])}</small></div>'
    team = "".join([
        person("Vinod M. Vokkarane", "Principal Investigator"), person("Orlando Arias", "Co-PI, hardware security"), person("Lewis Tseng", "Co-PI, distributed systems"),
        person("Yuzhang Lin", "Co-PI, NYU Tandon site"), person("Anurag Srivastava", "Co-PI, WVU site"), person("Yan Luo", "Senior personnel, networks"), person("Seung Woo Son", "Senior personnel, HPC"),
        person("Christopher Niezrecki", "Senior personnel, energy systems"),
    ])
    nav = ' '.join(f'<li><a href="index.html#{a}">{t}</a></li>' for a, t in [("about", "About"), ("research", "Research"), ("projects", "Projects"), ("sponsors", "Sponsors"), ("people", "People"), ("students", "Students"), ("alumni", "Alumni"), ("publications", "Publications"), ("news", "News"), ("contact", "Contact")])
    footer_html = footer_html.replace('href="#', 'href="index.html#')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SUMMIT: Secure and Resilient Multi-site Smart Grid Testbed | SCyPS, UMass Lowell</title>
<meta name="description" content="SUMMIT is an NSF Major Research Instrumentation Track 2 award building a three-site federated smart grid cybersecurity testbed across UMass Lowell, NYU Tandon, and West Virginia University, delivered as hardware-in-the-loop Simulation-as-a-Service.">
<meta property="og:title" content="SUMMIT: Secure and Resilient Multi-site Smart Grid Testbed">
<meta property="og:description" content="A three-site federated smart grid cybersecurity testbed across UMass Lowell, NYU Tandon, and West Virginia University, funded by the NSF Major Research Instrumentation program.">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE_URL}og-card.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}summit.html">
<link rel="alternate" type="application/rss+xml" title="SCyPS news" href="{SITE_URL}feed.xml">
{_ld(ld_summit())}
<link rel="preload" href="{FONT_ROOT}fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{FONT_ROOT}fonts/fraunces-latin-full-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{{font-family:"Fraunces";font-style:normal;font-weight:100 900;font-display:swap;src:url("{FONT_ROOT}fonts/fraunces-latin-full-normal.woff2") format("woff2")}}
@font-face{{font-family:"Fraunces";font-style:italic;font-weight:100 900;font-display:swap;src:url("{FONT_ROOT}fonts/fraunces-latin-full-italic.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-400-normal.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:italic;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-400-italic.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:500;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-500-normal.woff2") format("woff2")}}
@font-face{{font-family:"IBM Plex Sans";font-style:normal;font-weight:600;font-display:swap;src:url("{FONT_ROOT}fonts/ibm-plex-sans-latin-600-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:400;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-400-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:600;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-600-normal.woff2") format("woff2")}}
@font-face{{font-family:"Barlow";font-style:normal;font-weight:700;font-display:swap;src:url("{FONT_ROOT}fonts/barlow-latin-700-normal.woff2") format("woff2")}}
</style>

<link rel="icon" type="image/png" href="{img_src("favicon")}">
<style>{CSS}
.shero{{background:var(--navy);color:#fff;padding:clamp(48px,7vw,88px) 0 clamp(40px,6vw,64px)}}
.shero .kicker{{display:inline-block;background:#3BA995;color:#062B24;font-weight:600;font-size:13px;padding:4px 10px;border-radius:5px;margin-bottom:16px}}
.shero h1{{color:#fff;max-width:14em;font-size:clamp(34px,4.6vw,58px)}}
.shero p.sub{{font-size:clamp(17px,1.4vw,20px);color:#D6DEE8;max-width:40em;margin:18px 0 26px}}
.shero .facts{{margin-top:34px;background:transparent;border-color:rgba(255,255,255,.2);box-shadow:none}}
.shero .facts div{{border-color:rgba(255,255,255,.2)}} .shero .facts strong{{color:#fff}} .shero .facts span{{color:#B7C4D4}}
.archwrap{{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:18px 22px 12px;margin-top:-40px;position:relative;z-index:2;box-shadow:0 22px 60px -34px var(--shadow)}}
.archwrap img{{width:100%;height:auto;display:block}} .archwrap p{{font-size:13px;color:#5B6B82;text-align:center;margin:10px 0 0}}
.two{{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(24px,5vw,64px);align-items:start}}
.two h3{{margin-bottom:10px}} .two p,.two li{{color:var(--ink-2)}}
.plist2{{margin:0;padding-left:20px}} .plist2 li{{margin-bottom:10px}} .plist2 b{{color:var(--ink)}}
.instr{{display:grid;grid-template-columns:300px 1fr;gap:clamp(24px,4vw,56px);align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px}}
.instr img{{width:100%;height:auto;display:block;border-radius:10px;background:radial-gradient(ellipse at 50% 35%,#1A3D63,#0E2036 70%);padding:14px}}
.instr ul{{margin:8px 0 0;padding-left:18px;color:var(--ink-2)}}
.sites{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.site{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px}}
.site h3{{font-size:20px;margin-bottom:6px}} .site .role{{color:var(--signal-2);font-weight:600;font-size:13.5px;margin-bottom:8px}} .site p{{font-size:14.5px;color:var(--ink-2);margin:0}}
.teamgrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}}
.teamgrid .tm{{display:flex;flex-direction:column;justify-content:flex-start}}
.tm{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px;text-align:center}}
.tm .avatar{{margin:0 auto 12px;width:120px;height:120px}} .tm b{{display:block}} .tm span{{display:block;font-size:13.5px;color:var(--signal-2);font-weight:600}} .tm small{{display:block;font-size:12.5px;color:var(--ink-3);margin-top:4px}}
.phases{{list-style:none;margin:0;padding:0;border-top:2px solid var(--ink)}}
.phases li{{display:grid;grid-template-columns:150px 1fr;gap:20px;padding:14px 0;border-bottom:1px solid var(--line)}}
.phases b{{color:var(--ink-2)}} .phases p{{margin:0;color:var(--ink-2)}}
.cta2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.cta2 .box{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px}}
.cta2 h3{{margin-bottom:8px}} .cta2 p{{color:var(--ink-2);font-size:15px}}
@media (max-width:900px){{.two,.instr,.cta2{{grid-template-columns:1fr}}.sites{{grid-template-columns:1fr}}.teamgrid{{grid-template-columns:1fr 1fr}}.phases li{{grid-template-columns:1fr;gap:4px}}}}
</style>
<script>(function(){{try{{var t=localStorage.getItem('scyps-theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="SCyPS home"><span class="mark"><img src="{img_src("logo_mark")}" alt="" width="576" height="271"></span><span>SCyPS<small>Center for Smart Cyber-Physical Systems, UMass Lowell</small></span></a>
    <div class="navright">
    <ul class="links" id="menu">{nav}</ul>
    <a class="gift" href="{GIFT_URL}">Make a Gift</a>
    <button class="theme" id="theme" type="button" aria-label="Switch to dark mode"><svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></svg><span class="lbl">Dark</span></button>
    <button class="navtoggle" aria-expanded="false" aria-controls="menu">Menu</button>
    </div>
  </div>
</header>
<main id="main">
<div class="shero">
  <div class="wrap">
    <span class="kicker">NSF Major Research Instrumentation, Track 2</span>
    <h1>SUMMIT: a secure and resilient multi-site smart grid testbed</h1>
    <p class="sub">A federated instrument for research and training on attacks, defenses, and recovery in cyber-physical power systems, built by UMass Lowell with NYU Tandon and West Virginia University and delivered to collaborators as hardware-in-the-loop Simulation-as-a-Service.</p>
    <div class="cta"><a class="btn primary" href="{POSTDOC_URL}">Apply: postdoctoral research associate</a><a class="btn" href="mailto:vinod_vokkarane@uml.edu?subject=SUMMIT%20collaboration">Propose a collaboration</a><a class="btn" href="index.html">Back to SCyPS</a></div>
    <div class="facts">
      <div><strong>$2.0M</strong><span>NSF award #2511635; UMass Lowell share $1.56M with subawards to NYU and WVU</span></div>
      <div><strong>3 sites</strong><span>UMass Lowell (lead), NYU Tandon, West Virginia University</span></div>
      <div><strong>Oct 2026</strong><span>award start; three-year Phase 1 through Sept 2029</span></div>
      <div><strong>4 paradigms</strong><span>distributed HIL, Internet-in-the-loop, distributed digital twins, HIL Simulation-as-a-Service</span></div>
    </div>
  </div>
</div>
<div class="wrap"><figure class="archwrap"><img src="{img_src("summit_arch")}" alt="SUMMIT architecture diagram" width="1800" height="748"><p>SUMMIT architecture: the UMass Lowell main site with its real-time digital simulator and control, network, and instrumentation equipment; a wide-area software-defined network over the Internet; and the WVU and NYU federation sites.</p></figure></div>

<section id="overview">
  <div class="wrap">
    <div class="shead"><h2>What SUMMIT is</h2><p>A shared instrument that couples high-fidelity real-time simulation of the Northeast transmission grid with real control, networking, and cybersecurity hardware in the loop, at three universities linked over the Internet.</p></div>
    <div class="two">
      <div>
        <h3>Four paradigms</h3>
        <ol class="plist2">
          <li><b>Distributed hardware-in-the-loop (HIL) simulation.</b> Control, networking, and cybersecurity hardware closes the loop with grid models running in real time on RTDS simulators.</li>
          <li><b>Internet-in-the-loop simulation.</b> The three sites exchange live simulation signals over a wide-area software-defined network across the public Internet, so the network itself is part of every experiment.</li>
          <li><b>Heterogeneous distributed digital twins.</b> Scoped in Phase 1 to the RTDS simulators and the existing OPAL-RT simulator, which is relocated to UML North.</li>
          <li><b>Federated platform for HIL Simulation-as-a-Service.</b> The central objective. In Phase 1 the federation covers the three partner universities, with WVU's existing testbed as the first instrument federated. National-scale federation is planned for Phase 2.</li>
        </ol>
      </div>
      <div>
        <h3>Scope of Phase 1</h3>
        <p>Modeling and simulation focus on the backbone transmission grid of the Northeast; local distribution grids are left to future work. The instrument is built for high-fidelity real-time simulation with control, networking, and cybersecurity hardware in the loop, and it eliminates power hardware on site: no power amplifier, inverters, solar panels, batteries, microgrid, or drones. All power components are modeled at high fidelity inside the RTDS simulators.</p>
        <p>The cyber-physical grid instances built and tested on the simulators are small to medium scale for proof of concept, while keeping every capability needed to scale to the regional and national models originally planned. The physical asset monitoring thrust and the electric vehicle course are outside the funded scope for this phase; multimodal asset monitoring is planned for Phase 2.</p>
      </div>
    </div>
  </div>
</section>

<section id="instrument" class="tint">
  <div class="wrap">
    <div class="shead"><h2>The instrument</h2><p>Real-time digital simulation at the core, surrounded by the hardware that makes an experiment cyber-physical.</p></div>
    <div class="instr">
      <img src="{img_src("rtds")}" alt="RTDS NovaCor real-time digital simulator rack" width="507" height="760">
      <div>
        <h3>RTDS NovaCor real-time digital simulators</h3>
        <p>RTDS simulators run grid models at time steps small enough to drive real relays, controllers, and network devices in closed loop. Every power component, from generation and storage to inverters, lives inside the simulation, which is what lets the testbed stay safe, repeatable, and free of power hardware on site.</p>
        <p>Around the simulators at the UMass Lowell main site:</p>
        <ul>
          <li>Signal generator and grid simulator for excitation and disturbance injection</li>
          <li>Network emulator for latency, loss, and attack scenarios on the communication layer</li>
          <li>Optical, RF, and FPGA equipment for the transport and edge layers</li>
          <li>Control and GPS equipment for time synchronization and protection</li>
          <li>Core network switch and the control and monitoring workstations</li>
          <li>Wide-area SDN links to the WVU and NYU sites, each with its own switch, controller, and simulator</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="sites">
  <div class="wrap">
    <div class="shead"><h2>Three sites, one instrument</h2><p>Each site runs part of the grid and part of the experiment; the federation layer makes them behave as one testbed.</p></div>
    <div class="sites">
      <div class="site"><h3>UMass Lowell</h3><div class="role">Lead site and instrument host</div><p>Main site at UML North with the RTDS simulators, the relocated OPAL-RT simulator, control and instrumentation equipment, and the federation controller. Home of the Center for Smart Cyber-Physical Systems.</p></div>
      <div class="site"><h3>NYU Tandon School of Engineering</h3><div class="role">Federation site, Co-PI Yuzhang Lin</div><p>Power system modeling, state estimation, and cyber-physical resilience; the NYU node carries its own switch, controller, and simulator.</p></div>
      <div class="site"><h3>West Virginia University</h3><div class="role">Federation site, Co-PI Anurag Srivastava</div><p>WVU's existing grid testbed is the first external instrument federated into SUMMIT, the proof point for Simulation-as-a-Service.</p></div>
    </div>
  </div>
</section>

<section id="team" class="tint">
  <div class="wrap">
    <div class="shead"><h2>Team</h2><p>Faculty across three universities and three UMass Lowell departments.</p></div>
    <div class="teamgrid">{team}</div>
  </div>
</section>

<section id="plan">
  <div class="wrap">
    <div class="shead"><h2>Plan</h2><p>Phase 1 runs three years from October 2026. Milestones below are the planning targets; they will be updated as the project moves.</p></div>
    <ul class="phases">
      <li><b>Year 1, 2026 to 2027</b><p>Instrument acquisition and installation at UML North; RTDS commissioning; relocation of the OPAL-RT simulator; site network and control equipment; postdoctoral researcher joins to lead federation development.</p></li>
      <li><b>Year 2, 2027 to 2028</b><p>Three-site federation over the wide-area SDN; Internet-in-the-loop experiments; WVU testbed federated as the first external instrument; first shared attack, defense, and restoration experiments.</p></li>
      <li><b>Year 3, 2028 to 2029</b><p>HIL Simulation-as-a-Service opened to partner-university researchers and students; training modules; documentation and access process for future federation members.</p></li>
      <li><b>Phase 2, planned</b><p>National-scale federation, multimodal physical asset monitoring, and distribution-grid modeling.</p></li>
    </ul>
  </div>
</section>

<section id="join" class="tint">
  <div class="wrap">
    <div class="shead"><h2>Work on SUMMIT</h2><p>Openings for a postdoctoral researcher and graduate students, and a path for collaborators who want time on the instrument.</p></div>
    <div class="cta2">
      <div class="box"><h3>Postdoctoral research associate</h3><p>Lead the federation software and the Internet-in-the-loop experiments across the three sites, working with the PI and Co-PIs at UMass Lowell. Position open for Fall 2026.</p><a class="btn-gift summit-btn" href="{POSTDOC_URL}">View the posting and apply</a></div>
      <div class="box"><h3>Students and collaborators</h3><p>Ph.D. and M.S. students join through the UMass Lowell ECE program; write to a faculty member whose work matches yours and copy the director at <a href="mailto:Vinod_Vokkarane@uml.edu">Vinod_Vokkarane@uml.edu</a>. Researchers at other institutions who want to run experiments on SUMMIT once the federation opens should contact the PI.</p><a class="btn-gift summit-btn" href="mailto:vinod_vokkarane@uml.edu?subject=SUMMIT">Contact the PI</a></div>
    </div>
    <div class="ack" style="margin-top:32px"><p>This material is based upon work supported by the U.S. National Science Foundation under Grant No. 2511635. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.</p></div>
  </div>
</section>
</main>
{footer_html}
{script_html}
</body>
</html>
"""
    page = new_tab_links(page)
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out}: {len(page)/1024:.0f} KB")

if __name__ == "__main__":
    build()
