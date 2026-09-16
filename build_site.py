#!/usr/bin/env python3
"""Builds a single self-contained index.html for the SCyPS center site (image-rich version).

All publication and grant data live here so the HTML is generated without
hand-typed DOIs. Publications: Crossref (2025-2026) + UML faculty pages.
Grants: figures confirmed on the director's NSF Current & Pending (Sept 2026).
"""
import html, json, re

import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "index.html"   # run: python3 build_site.py [output path]

# ---------------------------------------------------------------- people
CORE = {"Vokkarane", "Arias", "Tseng", "Son", "Aghara", "Lin", "Luo", "Xie", "Cao", "Chigan", "Inalpolat", "Robinette", "Yu", "Akyurtlu", "Niezrecki", "Ranasingha"}
CORE_INITIAL = {"Son": "S", "Lin": "Y", "Luo": "Y", "Cao": "Y", "Yu": "H", "Xie": "Y"}   # common surnames: bold only with this first initial

FACULTY = {
    "director": {
        "name": "Vinod M. Vokkarane", "photo": "vokkarane", "title": "Professor, Electrical and Computer Engineering; Director, SCyPS",
        "areas": "Cyber-physical systems, smart grid cybersecurity and resilience, optical and 6G network optimization, AI/ML for networked systems",
        "email": "vinod_vokkarane@uml.edu", "phone": "978-934-3345", "office": "Ball Hall 409",
        "url": "https://www.uml.edu/engineering/electrical-computer/faculty/vokkarane-vinod.aspx",
        "bio": ("Vinod Vokkarane has directed the center since 2021. His group works on secure and resilient "
                "cyber-physical power systems, quality-of-transmission-aware multi-band and space-division "
                "multiplexed optical networks, and open-source tools for reproducible network research. He is a "
                "Senior Member of the IEEE, serves on the editorial board of the IEEE/Optica Journal of Optical "
                "Communications and Networking, co-authored the Springer book Optical Burst Switched Networks, and "
                "has shared best paper awards at IEEE GLOBECOM, IEEE ANTS, and ONDM. He is the PI of the NSF MRI "
                "SUMMIT testbed award and a technical advisor to the UMass Lowell Applied Research Corporation (UMLARC)."),
    },
    "core": [
        {"name": "Orlando Arias", "photo": "arias", "title": "Assistant Professor, Electrical and Computer Engineering",
         "areas": "Hardware security, hardware-software co-design, embedded and microarchitectural security, cyber security",
         "email": "Orlando_Arias@uml.edu", "phone": "978-934-3476", "office": "Ball Hall 407A",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/arias-orlando.aspx",
         "role": "Co-PI on the SUMMIT testbed and the ONR post-disaster restoration project; leads hardware attestation and embedded security for grid devices."},
        {"name": "Sukesh Aghara", "photo": "aghara", "title": "Professor, Chemical (Nuclear) Engineering; Director, Nuclear Engineering Program",
         "areas": "Nuclear nonproliferation, nuclear security and safeguards, nuclear energy for decarbonization", "email": "Sukesh_Aghara@uml.edu", "phone": "978-934-3115", "role": "Leads the Massachusetts Advanced Nuclear and Fusion Energy Roadmaps; directs the Integrated Nuclear Security and Safeguards Laboratory (INSSL) and co-directs the IAEA-funded Intercontinental Nuclear Institute.", "url": "https://www.uml.edu/engineering/chemical/faculty/aghara-sukesh.aspx"},

        {"name": "Seung Woo Son", "photo": "son", "title": "Associate Professor, Electrical and Computer Engineering",
         "areas": "High performance computing, parallel I/O and data-intensive computing, compiler optimizations, embedded systems",
         "email": "SeungWoo_Son@uml.edu", "phone": "978-934-6846", "office": "Ball Hall 419",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/son-seung-woo.aspx",
         "role": "NSF CAREER awardee (2018); brings HPC, silent-data-corruption detection, and on-device stream analytics to the center's data-intensive CPS work."},
        {"name": "Lewis Tseng", "photo": "tseng", "title": "Associate Professor, Electrical and Computer Engineering",
         "areas": "High-performance fault-tolerant distributed systems, blockchain-based systems, intelligent traffic and vehicular computing",
         "email": "Lewis_Tseng@uml.edu", "phone": "", "office": "Ball Hall, 3rd floor",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/tseng-lewis.aspx",
         "role": "NSF CAREER awardee (2023) on fault-tolerant edge computing for cyber-physical systems under cyber attack; Co-PI on SUMMIT. Joined UMass Lowell in 2024 after Clark University, Boston College, and Toyota InfoTechnology Center."},
        {"name": "Yuzhang Lin", "photo": "lin", "inst": "New York University", "title": "Assistant Professor, Electrical and Computer Engineering, NYU Tandon School of Engineering",
         "areas": "Smart grid and renewable energy: modeling, situational awareness, cyber-physical resilience, machine learning applications",
         "email": "yuzhang.lin@nyu.edu", "phone": "", "office": "",
         "url": "https://engineering.nyu.edu/faculty/yuzhang-lin",
         "role": "External center member; UMass Lowell ECE faculty 2018 to 2023. NSF CAREER awardee; Co-PI on SUMMIT and the ONR post-disaster restoration project, and a co-author on the center's smart grid papers."},
        {"name": "Yan Luo", "photo": "luo", "title": "Professor, Electrical and Computer Engineering; Robotics",
         "areas": "Computer architecture, network systems", "email": "yan_luo@uml.edu", "phone": "978-934-2592", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/luo-yan.aspx"},
        {"name": "Yuanchang Xie", "photo": "xie", "title": "Professor, Civil and Environmental Engineering",
         "areas": "Transportation engineering, smart and connected transportation", "email": "Yuanchang_Xie@uml.edu", "phone": "978-934-3681", "url": "https://www.uml.edu/engineering/civil-environmental/faculty-staff-students/faculty/xie-yuanchang.aspx"},    ],
    "affiliated": [
        {"name": "Yu Cao", "photo": "cao", "title": "Professor, Miner School of Computer and Information Sciences; Director, UMass Center for Digital Health",
         "areas": "Medical imaging, multimodal deep learning, computer vision, AI, digital health", "email": "yu_cao@uml.edu", "phone": "978-934-3628", "url": "https://www.uml.edu/sciences/computer-science/people/cao-yu.aspx"},
        {"name": "Chunxiao (Tricia) Chigan", "photo": "chigan", "title": "Professor, Electrical and Computer Engineering",
         "areas": "Communication networks and network security", "email": "Tricia_Chigan@uml.edu", "phone": "978-934-3364", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/chigan-tricia.aspx"},
        {"name": "Murat Inalpolat", "photo": "inalpolat", "title": "Professor, Mechanical and Industrial Engineering; Associate Chair for Doctoral Studies",
         "areas": "Structural health monitoring, diagnostics and prognostics, structural dynamics, vibrations, acoustics, signal processing", "email": "Murat_Inalpolat@uml.edu", "phone": "978-934-2556", "url": "https://www.uml.edu/engineering/mechanical-industrial/faculty/inalpolat-murat.aspx"},
        {"name": "Paul Robinette", "photo": "robinette", "title": "Associate Professor, Electrical and Computer Engineering; Associate Chair for M.S. Programs",
         "areas": "Robotics, human-robot interaction; Printed Electronics Research Collaborative; Raytheon UMass Lowell Research Institute", "email": "Paul_Robinette@uml.edu", "phone": "978-934-3347", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/robinette-paul.aspx"},
        {"name": "Hengyong Yu", "photo": "yu", "title": "Professor, Electrical and Computer Engineering",
         "areas": "Biomedical imaging, medical image reconstruction, image processing and analysis", "email": "Hengyong_Yu@uml.edu", "phone": "978-934-6756", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/yu-hengyong.aspx"},
        {"name": "Alkim Akyurtlu", "photo": "akyurtlu", "title": "Professor, Electrical and Computer Engineering; Director, Raytheon UMass Lowell Research Institute (RURI); Director, Printed Electronics Research Collaborative (PERC)",
         "areas": "Additive manufacturing and printed electronics for RF and microwave devices, wearables, functional printable inks, metamaterials", "email": "Alkim_Akyurtlu@uml.edu", "phone": "978-934-3336", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/akyurtlu-alkim.aspx"},
        {"name": "Christopher Niezrecki", "photo": "niezrecki", "title": "Distinguished University Professor, Mechanical and Industrial Engineering; Director, Center for Energy Innovation; Co-director, Rist Institute for Sustainability and Energy",
         "areas": "Renewable energy systems, wind turbine dynamics, structural health monitoring and inspection, structural dynamics and acoustics, smart materials", "email": "Christopher_Niezrecki@uml.edu", "phone": "978-934-2963", "url": "https://www.uml.edu/engineering/mechanical-industrial/faculty/niezrecki-christopher.aspx"},
        {"name": "Oshadha Ranasingha", "photo": "ranasingha", "title": "Assistant Professor, Electrical and Computer Engineering; PERC and RURI",
         "areas": "Functional inks for printed electronics and additive manufacturing, fully printed micro-supercapacitors, energy harvesting, hardware authentication", "email": "oshadha_ranasingha@uml.edu", "phone": "978-934-2336", "url": "https://www.uml.edu/engineering/electrical-computer/faculty/ranasingha-oshadha.aspx"},
    ],
    "external": [
        {"name": "Anurag Srivastava", "tag": "External collaborator", "photo": "srivastava", "inst": "West Virginia", "title": "Raymond J. Lane Professor and Chairperson, Lane Department of Computer Science and Electrical Engineering, West Virginia University; IEEE Fellow",
         "areas": "Data-driven algorithms for power system operation, control, and resilience; WVU partner on the SUMMIT federated smart grid testbed",
         "email": "anurag.srivastava@mail.wvu.edu", "phone": "", "url": "https://directory.statler.wvu.edu/faculty-staff-directory/anurag-srivastava"},
        {"name": "Heidi Dempsey", "tag": "External collaborator", "photo": "dempsey", "inst": None, "title": "Research Director of the Northeast US, Red Hat",
         "areas": "Grows research and open-source collaborations between Red Hat and academic partners; Red Hat partner for the center's Friendly Fedora and Podman work",
         "email": "hdempsey@redhat.com", "phone": "", "url": "https://www.bu.edu/hic/profile/heidi-dempsey/"},
        {"name": "Babu Jain", "tag": "External collaborator", "photo": "jain", "inst": None, "title": "Founder and CEO, Navia Energy Inc.",
         "areas": "AI-driven renewable energy systems; industry partner on the center's resilient smart grids project",
         "email": "", "phone": "", "url": "https://www.linkedin.com/in/babu-jain-188470/"},
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
     "title": "SUMMIT: A Secure and Resilient Multi-site Smart Grid Testbed for Multidisciplinary Research and Training",
     "amount": "$2.0M", "share": "UMass Lowell share $1.56M", "period": "Oct 2026 to Sep 2029",
     "team": "PI Vinod Vokkarane; Co-PIs Orlando Arias, Lewis Tseng (UMass Lowell), Yuzhang Lin (NYU); partner site West Virginia University",
     "desc": ("A federated cyber-physical testbed that links RTDS real-time simulation of the Northeast transmission grid with control, "
              "networking, and cybersecurity hardware in the loop across three universities over a wide-area SDN, delivered as "
              "HIL Simulation-as-a-Service. A postdoctoral researcher will lead federation development."),
     "domain": "Energy"},
    {"tag": "New in 2026", "sponsor": "Massachusetts Technology Collaborative, Applied AI Models program",
     "title": "ARPO-Sensor Fusion: Autonomous Robotic Planning and Optimization for Intelligence Sensor Fusion",
     "amount": "$625K", "period": "Sep 2026 to Aug 2027",
     "team": "PI Vinod Vokkarane; performed at UMLARC",
     "desc": "Applied AI models that fuse multi-sensor intelligence feeds to plan and optimize autonomous robotic missions.",
     "domain": "Autonomy"},
    {"tag": "New in 2026", "sponsor": "U.S. Army",
     "title": "ARPO: Autonomous Robotic Planning and Optimization",
     "amount": "$225K", "period": "Mar 2026 to Jul 2027",
     "team": "PI Vinod Vokkarane; UMLARC and UMass Lowell",
     "desc": "Planning and optimization methods for autonomous robotic systems operating over contested tactical networks.",
     "domain": "Autonomy"},
    {"tag": "Completed", "sponsor": "Office of Naval Research",
     "title": "Unified Post-Disaster Restoration Planning for Cyber-Physical Power Distribution Systems",
     "amount": "$550K", "period": "Jan 2024 to Oct 2025",
     "team": "PI Vinod Vokkarane; Co-PIs Orlando Arias (UMass Lowell), Yuzhang Lin (NYU)",
     "desc": ("Joint restoration of the power and communication layers of a distribution grid after a disaster, "
              "including networked microgrid formation and communication-aware state recovery."),
     "domain": "Energy"},
    {"tag": "Active", "sponsor": "U.S. Department of Energy",
     "title": "CyberCARE: Northeast University Cybersecurity Center for Advanced and Resilient Energy Delivery",
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
    {"tag": "Active", "sponsor": "National Science Foundation, CAREER",
     "title": "Towards Fault-tolerant Edge Computing for Cyber-Physical Systems: Distributed Primitives for Coordination under Cyber Attacks",
     "amount": "About $500K", "period": "2023 onward",
     "team": "PI Lewis Tseng",
     "desc": "Coordination primitives that let edge computing systems keep working when some nodes are faulty or compromised.",
     "domain": "Edge"},
    {"tag": "Completed", "sponsor": "Office of Naval Research",
     "title": "Software-Defined Cyber-Physical Microgrids (SDCPM) for Agile Adaptation to High-Impact, Low-Probability Disturbances",
     "amount": "$300K", "period": "2021 to 2024",
     "team": "PI Vinod Vokkarane",
     "desc": "Software-defined control of cyber-physical microgrids so they can reconfigure quickly around rare, high-impact disturbances.",
     "domain": "Energy"},
    {"tag": "Completed", "sponsor": "National Science Foundation, CNS Core",
     "title": "Flexible Spectrum Allocation in Next-Generation Optical Networks",
     "amount": "$350K", "share": "plus a $16K REU supplement", "period": "2020 to 2024",
     "team": "PI Vinod Vokkarane",
     "desc": "Spectrum allocation algorithms for elastic optical networks, the line of work that led to the FUSION simulator.",
     "domain": "Networks"},
    {"tag": "Completed", "sponsor": "Office of Naval Research",
     "title": "Resilient Sensing and Communication Architecture for Naval Energy Infrastructure Monitoring",
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
    {"name": "FUSION", "what": "Open-source benchmarking and simulation framework for reproducible optical network research (routing, spectrum and space assignment, QoT models). Described in JOCN, Sept. 2026."},
    {"name": "Containerized grid co-simulation testbed", "what": "Docker-packaged HELICS, GridLAB-D, and ns-3 federation for cyber-physical power studies on the IEEE 123-bus feeder, with DNP3 traffic between control center and devices."},
    {"name": "SUMMIT (in development)", "what": "Three-site federated smart grid testbed built around RTDS real-time simulators and a wide-area SDN, funded by the NSF MRI award and opening in 2026-2027 to collaborators as HIL Simulation-as-a-Service."},
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
pub(2023, ["G. Cheng", "Y. Lin", "J. Zhao", "J. Yan"],
    "A Highly Discriminative Detector against False Data Injection Attacks in AC State Estimation",
    "IEEE Power & Energy Society General Meeting (PESGM)", "pp. 1-1, July 2023",
    "10.1109/pesgm52003.2023.10252930", "conference", ["Lin"], "Smart grid")
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
    "IEEE Transactions on Instrumentation and Measurement", "vol. 70, pp. 1-10, 2021",
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

MONTHS = {"Jan.":1,"Feb.":2,"Mar.":3,"Apr.":4,"May":5,"June":6,"July":7,"Aug.":8,"Sept.":9,"Oct.":10,"Nov.":11,"Dec.":12}
def month_of(p):
    for k, v in MONTHS.items():
        if re.search(r'\b' + re.escape(k) + r'(?=\s+\d{4})', p["details"]): return v
    return 0
P.sort(key=lambda p: (-p["year"], -month_of(p), 0 if p["type"] == "journal" else 1, p["title"].lower()))

NEWS = [
    ("Oct 2026", "SUMMIT begins. NSF's $2M Major Research Instrumentation Track 2 award funds a three-site federated smart grid testbed with NYU and West Virginia University, starting October 1, 2026; a postdoctoral search is under way."),
    ("Sep 2026", "The FUSION benchmarking framework paper appears in JOCN's special issue on benchmarking in optical networks, followed in October by a QoT-aware grooming paper for multi-band SDM networks."),
    ("Sep 2026", "ARPO-Sensor Fusion starts under the Massachusetts Technology Collaborative's Applied AI Models program ($625K), performed at UMLARC."),
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
    lines.append('<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in meta) + '</p>')
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
.skip{position:absolute;left:-999px;top:8px;background:var(--navy);color:#fff;padding:8px 12px;z-index:100}
.skip:focus{left:8px}

/* nav */
.nav{position:sticky;top:0;z-index:50;background:var(--nav-bg);backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:66px;gap:12px}
.brand{display:flex;align-items:center;gap:10px;color:var(--ink);font-family:"Fraunces",Georgia,serif;font-size:19px;font-weight:600;letter-spacing:-.01em;min-width:0;flex:0 1 auto;overflow:hidden}
.brand>span{white-space:nowrap;min-width:0;overflow:hidden;text-overflow:ellipsis}
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
@media (max-width:1460px){.brand small{display:none}}
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
.flow.slow{animation-duration:4.2s}
@keyframes flow{to{stroke-dashoffset:-48}}
.pulse{animation:pulse 3s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
.spin{animation:spin 7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.grow{animation:grow 3.2s ease-in-out infinite}
@keyframes grow{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.72)}}
.trace{stroke-dasharray:120 160;animation:trace 2.4s linear infinite}
@keyframes trace{to{stroke-dashoffset:-280}}
@media (prefers-reduced-motion:reduce){.flow,.pulse,.spin,.grow,.trace{animation:none}.flow{stroke-dasharray:none}.trace{stroke-dasharray:none}}

/* research */
.thrusts{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.thrust{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
.thrust .art{aspect-ratio:2/1;background:linear-gradient(160deg,var(--illus-bg),var(--illus-bg-2));color:var(--ink);border-bottom:1px solid var(--line);padding:6px}
.thrust .art svg{width:100%;height:100%;display:block}
.thrust .art .s-ink{stroke:var(--ink)} .thrust .art .f-ink{fill:var(--ink)} .thrust .art .f-surface{fill:var(--surface)} .thrust .art .f-muted{fill:var(--ink-3)}
.thrust .art .card{filter:drop-shadow(0 4px 10px rgba(4,73,120,.10))}
:root[data-theme="dark"] .thrust .art .card{filter:drop-shadow(0 4px 10px rgba(0,0,0,.4))}
.thrust .art .f-alert{fill:#E25555} .thrust .art .s-alert{stroke:#E25555} .thrust .art .f-alert-tint{fill:#FDECEC}
:root[data-theme="dark"] .thrust .art .f-alert-tint{fill:#3A1E20}
.thrust .art .s-sig{stroke:var(--signal)} .thrust .art .f-sig{fill:var(--signal)} .thrust .art .f-brand{fill:var(--brand-blue)} .thrust .art .s-brand{stroke:var(--brand-blue)} .thrust .art .f-grn{fill:var(--green)} .thrust .art .s-grn{stroke:var(--green)} .thrust .art .f-tint{fill:var(--bg-2)} .thrust .art .s-line{stroke:var(--line)} .thrust .art .f-line{fill:var(--line)} .thrust .art .f-sigt{fill:var(--signal-tint)} .thrust .art .f-amb{fill:var(--amber)} .thrust .art .s-amb{stroke:var(--amber)} .thrust .art .s-muted{stroke:var(--ink-3)}
.thrust .body{padding:22px 24px 24px;display:flex;flex-direction:column;flex:1}
.thrust h3{font-size:20px;margin-bottom:8px}
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
.feature .paradigms{padding:clamp(28px,4vw,52px) clamp(24px,3vw,40px) clamp(28px,4vw,52px) 0;border-left:1px solid rgba(255,255,255,.15);padding-left:clamp(24px,3vw,40px)}
.feature .paradigms h4{color:#fff;font-size:18px;margin-bottom:12px}
.feature .paradigms ol{margin:0 0 14px;padding-left:20px;color:var(--on-navy-2);font-size:14.5px;line-height:1.5}
.feature .paradigms li{margin-bottom:9px}
.feature .paradigms li b{color:#fff;font-weight:600}
.feature .paradigms .scope{font-size:13.5px;color:var(--on-navy-3);margin:0}
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
.proj .desc{margin:0 0 8px;color:var(--ink-2);max-width:60em}
.proj .team{font-size:14px;color:var(--ink-3);margin:0}
.proj .amt{text-align:right;font-family:"Fraunces",Georgia,serif;font-size:22px;font-weight:600;letter-spacing:-.01em;line-height:1.15}
.proj .amt small{display:block;font-family:"IBM Plex Sans",Arial,sans-serif;font-weight:400;font-size:13px;color:var(--ink-3);margin-top:6px;letter-spacing:0}
@media (max-width:860px){.proj{grid-template-columns:1fr}.proj .amt{text-align:left}}
.tools{margin-top:52px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.tool{background:var(--bg-2);border-radius:var(--radius);padding:22px 22px 24px;border:1px solid var(--line)}
.tool h4{font-size:17px;margin-bottom:6px}
.tool p{font-size:14.5px;color:var(--ink-2);margin:0}
@media (max-width:760px){.tools{grid-template-columns:1fr}}

/* people */
.avatar{border-radius:14px;object-fit:cover;display:block;background:var(--line-2);flex:none}
.avatar.xl{width:min(100%,300px);aspect-ratio:1/1;border-radius:18px}
.avatar.lg{width:112px;height:112px}
.avatar.sm{width:76px;height:76px;border-radius:10px}
.avatar.mono{display:grid;place-items:center;font-family:"Fraunces",Georgia,serif;font-weight:600;color:var(--ink-2);background:var(--signal-tint)}
.avatar.mono.sm{font-size:20px}
.director{display:grid;grid-template-columns:300px minmax(0,1fr);gap:clamp(24px,4vw,56px);padding:34px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);align-items:start}
.director .bio{color:var(--ink-2);max-width:48em;margin-top:14px}
.director .bio p{margin:0}
.person h3{margin-bottom:4px}
.ptitle{color:var(--ink-2);font-size:14.5px;margin-bottom:8px}
.pareas{font-size:15px;margin-bottom:8px}
.prole{font-size:14.5px;color:var(--ink-2);margin-bottom:8px}
.pmeta{font-size:13.5px;color:var(--ink-3);margin:0;display:flex;flex-wrap:wrap;gap:4px 0}
.pmeta .mi::after{content:"\00a0\00b7\00a0";color:var(--line)}
.pmeta .mi:last-child::after{content:""}
.metrics{display:flex;gap:6px 14px;flex-wrap:wrap;font-size:13px;color:var(--ink-3);margin-top:10px;min-height:0}
.metrics:empty{display:none}
.metrics b{color:var(--ink);font-weight:600}
.metrics .src{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:1px 6px;letter-spacing:.02em}
@media (max-width:760px){.director{grid-template-columns:1fr;padding:22px}}
.core{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-top:18px}
.core .person{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px}
.core .avatar{margin-bottom:16px}
.core .avatar.lg{width:128px;height:128px}
@media (max-width:860px){.core{grid-template-columns:1fr}}
.group{margin-top:48px}
.group h3{font-size:22px;margin-bottom:6px}
.group>p{color:var(--ink-3);font-size:14.5px;margin-bottom:14px}
.plist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.prow{display:flex;gap:16px;padding:16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);align-items:flex-start}
.pname{font-weight:600;display:block}
.ptag{display:inline-block;margin-left:8px;vertical-align:3px;font-family:"IBM Plex Sans",Arial,sans-serif;letter-spacing:0;font-size:11.5px;font-weight:500;padding:2px 8px;border-radius:999px;background:var(--signal-tint);color:var(--signal-2)}
.ptitle2{color:var(--ink-2);font-size:14px;display:block}
.pareas2{display:block;font-size:13.5px;color:var(--ink-3);margin-top:3px}
.pcontact{font-size:13px;color:var(--ink-3);margin-top:6px}
.pcontact .sep::before{content:"\00b7";margin:0 6px}
@media (max-width:860px){.plist{grid-template-columns:1fr}}
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

/* students and alumni */
.stugrid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.stugrid.two{grid-template-columns:repeat(2,1fr);margin-bottom:40px}
.stu{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px 22px 20px}
.stu .avatar{margin-bottom:14px;width:96px;height:96px;font-size:26px}
.avatar.round{border-radius:50%;background:transparent}
.avatar.mono.round{background:var(--signal-tint)}
.stu h3{font-size:20px;margin-bottom:4px}
.stu .focus{font-size:14.5px;color:var(--ink-2);margin:6px 0 8px}
.stu.feat{display:grid;grid-template-columns:96px 1fr;gap:6px 18px;align-items:start}
.stu.feat .avatar{grid-row:1/4;margin:0}
.stu.feat .focus{grid-column:2}
@media (max-width:980px){.stugrid{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.stugrid,.stugrid.two{grid-template-columns:1fr}.stu.feat{grid-template-columns:1fr}.stu.feat .avatar{grid-row:auto;margin-bottom:12px}.stu.feat .focus{grid-column:auto}}
.lablife{margin-top:52px}
.lablife h3{font-size:22px;margin-bottom:4px}
.lablife>p{color:var(--ink-3);font-size:14.5px;margin-bottom:14px}
.labgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.labgrid img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:var(--radius);border:1px solid var(--line);display:block}
@media (max-width:760px){.labgrid{grid-template-columns:1fr 1fr}}
.alumcols{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(24px,5vw,64px)}
.alumcols h3{font-size:22px;margin-bottom:10px}
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
.uml-footer.no-fa .social a{width:auto;height:auto;border-radius:6px;padding:6px 10px;font-size:13px;border-color:rgba(255,255,255,.35)}
.uml-footer.no-fa .social .label{position:static;width:auto;height:auto;clip:auto}
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
SCHEMATIC = """<svg viewBox="0 0 760 470" role="img" aria-labelledby="schemTitle schemDesc" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, Arial, sans-serif">
<title id="schemTitle">How a smart cyber-physical system closes the loop</title>
<desc id="schemDesc">Physical systems in energy, transportation, and healthcare are sensed at the edge, connected over a secure network, analysed by AI and high-performance computing, and controlled in real time.</desc>
<defs>
  <marker id="arrI" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0E2036"/></marker>
  <marker id="arrS" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#0A777F"/></marker>
  <marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1 10 5 0 9z" fill="#3BA995"/></marker>
</defs>

<!-- column headers -->
<g font-size="13" font-weight="600" fill="#5B6B82" letter-spacing=".02em">
  <text x="105" y="34" text-anchor="middle">PHYSICAL WORLD</text><text x="392" y="34" text-anchor="middle">SECURE NETWORK</text><text x="622" y="34" text-anchor="middle">COMPUTE AND CONTROL</text>
</g>
<g stroke="#D5DCE5" stroke-width="1"><path d="M30 44h150M317 44h150M512 44h220"/></g>

<!-- domain cards -->
<g class="card">
  <rect x="30" y="62" width="150" height="96" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <g transform="translate(48,74)" fill="none" stroke="#044978" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 44V14l16-8 16 8v30M6 44h32M14 24h16M14 33h16"/>
  </g>
  <path d="M112 78l-10 16h8l-6 16 16-20h-8l6-12z" fill="#3BA995"/>
  <text x="105" y="146" text-anchor="middle" font-size="13.5" font-weight="600" fill="#0E2036">Energy and power</text>
</g>
<g class="card">
  <rect x="30" y="192" width="150" height="96" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <g transform="translate(60,206)">
    <path d="M6 30h60l-9-17H16z" fill="#044978"/><path d="M0 30h72v8H0z" fill="#044978" opacity=".85"/>
    <circle cx="16" cy="40" r="6" fill="#fff" stroke="#044978" stroke-width="2"/><circle cx="56" cy="40" r="6" fill="#fff" stroke="#044978" stroke-width="2"/>
    <g fill="none" stroke="#3BA995" stroke-width="2" stroke-linecap="round"><path d="M28 8a10 10 0 0 1 16 0M22 2a18 18 0 0 1 28 0"/></g>
  </g>
  <text x="105" y="276" text-anchor="middle" font-size="13.5" font-weight="600" fill="#0E2036">Transportation</text>
</g>
<g class="card">
  <rect x="30" y="322" width="150" height="96" rx="12" fill="#fff" stroke="#D5DCE5"/>
  <circle cx="86" cy="362" r="19" fill="#0A777F"/><path d="M86 352v20M76 362h20" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
  <path d="M108 366h8l5-10 7 20 6-14 4 6h10" fill="none" stroke="#3BA995" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="105" y="406" text-anchor="middle" font-size="13.5" font-weight="600" fill="#0E2036">Healthcare</text>
</g>

<!-- edge nodes -->
<g class="card">
  <rect x="212" y="96" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/><rect x="212" y="226" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/><rect x="212" y="356" width="62" height="30" rx="15" fill="#fff" stroke="#0A777F" stroke-width="1.6"/>
</g>
<g font-size="12.5" font-weight="600" fill="#0A777F" text-anchor="middle"><text x="243" y="115">edge</text><text x="243" y="245">edge</text><text x="243" y="375">edge</text></g>

<!-- sense links: card -> edge -->
<g fill="none" stroke="#D5DCE5" stroke-width="2"><path d="M180 111h32M180 241h32M180 371h32"/></g>
<g fill="none" stroke="#3BA995" stroke-width="2.6" stroke-linecap="round"><path class="flow" d="M180 111h32"/><path class="flow slow" d="M180 241h32"/><path class="flow" d="M180 371h32"/></g>

<!-- network core -->
<g class="card">
  <circle cx="378" cy="241" r="74" fill="#fff" stroke="#044978" stroke-width="1.6"/>
  <circle cx="378" cy="241" r="74" fill="none" stroke="#0A777F" stroke-width="3" class="flow slow"/>
  <g stroke="#D5DCE5" stroke-width="1.2"><path d="M378 167v148M314 204l128 74M314 278l128-74"/></g>
  <g fill="#044978"><circle cx="378" cy="167" r="5.5"/><circle cx="442" cy="204" r="5.5"/><circle cx="442" cy="278" r="5.5"/><circle cx="378" cy="315" r="5.5"/><circle cx="314" cy="278" r="5.5"/><circle cx="314" cy="204" r="5.5"/></g>
  <circle cx="378" cy="241" r="14" fill="#0A777F"/><circle cx="378" cy="241" r="5" fill="#fff"/>
</g>
<text x="378" y="148" text-anchor="middle" font-size="12.5" fill="#5B6B82">optical and 5G/6G transport</text>
<text x="378" y="338" text-anchor="middle" font-size="12.5" fill="#5B6B82">zero trust, attestation, intrusion detection</text>

<!-- edge -> core links -->
<g fill="none" stroke="#D5DCE5" stroke-width="2"><path d="M274 111C296 111 302 172 316 200"/><path d="M274 241h30"/><path d="M274 371C296 371 302 310 316 282"/></g>
<g fill="none" stroke="#0A777F" stroke-width="2.6" stroke-linecap="round"><path class="flow" d="M274 111C296 111 302 172 316 200"/><path class="flow slow" d="M274 241h30"/><path class="flow" d="M274 371C296 371 302 310 316 282"/></g>

<!-- compute card -->
<g class="card">
  <rect x="512" y="132" width="220" height="218" rx="14" fill="#fff" stroke="#D5DCE5"/>
  <rect x="512" y="132" width="220" height="44" rx="14" fill="#044978"/><rect x="512" y="160" width="220" height="16" fill="#044978"/>
  <text x="622" y="160" text-anchor="middle" font-size="14" font-weight="600" fill="#fff">AI, digital twins, HPC</text>
  <g fill="#F3F7FA" stroke="#D5DCE5"><rect x="528" y="190" width="188" height="34" rx="8"/><rect x="528" y="234" width="188" height="34" rx="8"/><rect x="528" y="278" width="188" height="34" rx="8"/></g>
  <g fill="none" stroke="#0A777F" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M540 212l6-8 5 5 6-10 5 6"/><path d="M539 256h8l4-8 4 12 4-6h8"/><path d="M540 302l7-7 5 5 9-9M563 291h-6v6"/>
  </g>
  <g font-size="12.5" fill="#0E2036"><text x="576" y="211">Anomaly detection</text><text x="576" y="255">State estimation</text><text x="576" y="299">Plan and optimize</text></g>
  <g fill="#3BA995"><circle cx="702" cy="207" r="4" class="pulse"/><circle cx="702" cy="251" r="4" class="pulse" style="animation-delay:1s"/><circle cx="702" cy="295" r="4" class="pulse" style="animation-delay:2s"/></g>
  <text x="622" y="336" text-anchor="middle" font-size="12" fill="#5B6B82">edge to cloud</text>
</g>

<!-- core <-> compute -->
<g fill="none" stroke="#0A777F" stroke-width="2.2"><path d="M454 226h50" marker-end="url(#arrS)"/></g>
<g fill="none" stroke="#3BA995" stroke-width="2.2"><path d="M506 256h-50" marker-end="url(#arrG)"/></g>
<text x="481" y="215" text-anchor="middle" font-size="11.5" fill="#5B6B82">telemetry</text>
<text x="481" y="275" text-anchor="middle" font-size="11.5" fill="#5B6B82">control</text>

<!-- return loop -->
<path d="M622 350v70H105v-2" fill="none" stroke="#3BA995" stroke-width="2" stroke-dasharray="5 6" marker-end="url(#arrG)"/>
<text x="392" y="452" text-anchor="middle" font-size="12.5" fill="#5B6B82">closed loop: sense, communicate, decide, act</text>
</svg>"""

ICONS = {
    "grid": '<svg viewBox="0 0 40 40"><path d="M6 34V14l14-8 14 8v20M6 34h28M14 22h12M14 28h12"/><path d="M4 36h32"/></svg>',
    "ai": '<svg viewBox="0 0 40 40"><rect x="8" y="8" width="24" height="24" rx="4"/><path d="M16 8V4M24 8V4M16 36v-4M24 36v-4M8 16H4M8 24H4M36 16h-4M36 24h-4"/><path d="M15 20h10M20 15v10"/></svg>',
    "fiber": '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="14"/><path d="M6 20h28M20 6c6 6 6 22 0 28M20 6c-6 6-6 22 0 28"/></svg>',
    "edge": '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="4"/><circle cx="8" cy="10" r="3"/><circle cx="32" cy="10" r="3"/><circle cx="8" cy="30" r="3"/><circle cx="32" cy="30" r="3"/><path d="M11 12l6 5M29 12l-6 5M11 28l6-5M29 28l-6-5"/></svg>',
    "chip": '<svg viewBox="0 0 40 40"><rect x="12" y="12" width="16" height="16" rx="2"/><path d="M16 12V6M20 12V6M24 12V6M16 34v-6M20 34v-6M24 34v-6M12 16H6M12 20H6M12 24H6M34 16h-6M34 20h-6M34 24h-6"/></svg>',
    "health": '<svg viewBox="0 0 40 40"><path d="M4 22h8l4-10 6 18 4-10h10"/><rect x="6" y="6" width="28" height="28" rx="5"/></svg>',
}

THRUSTS = [
    ("grid", "Smart grid cybersecurity and resilience",
     "Attack-aware dispatch, false-data-injection detection in smart meters, observability-aware PMU networking, and joint power-communication restoration after disasters. Anchored by the SUMMIT federated testbed.",
     "Vokkarane, Arias, Tseng, Lin"),
    ("ai", "AI and agentic systems for cyber-physical control",
     "Machine learning for intrusion detection and state recovery, physics-grounded models for network provisioning, and safety enforcement for AI agents that touch physical infrastructure.",
     "Vokkarane, Cao, Son"),
    ("fiber", "Next-generation optical and 6G transport",
     "Multi-band and space-division multiplexed elastic optical networks, quality-of-transmission-aware resource allocation and grooming, service prioritization for 6G transport, and the open-source FUSION framework.",
     "Vokkarane, Chigan"),
    ("edge", "Fault-tolerant distributed and edge computing",
     "Consensus and state machine replication that stay correct under crashes and attacks, blockchain systems, satellite-edge drone coordination, and digital twins delivered from hybrid clouds.",
     "Tseng, Luo"),
    ("chip", "Hardware security and high performance computing",
     "Hardware trojan detection at RTL, silent data corruption detection from hardware counters, attested embedded devices for grid edges, and parallel I/O for data-intensive science.",
     "Arias, Son"),
    ("health", "Connected transportation, health, and infrastructure",
     "Intelligent traffic and vehicular computing, medical imaging and digital health platforms, structural health monitoring, nuclear security, and robotics for critical facilities.",
     "Xie, Tseng, Cao, Yu, Inalpolat, Aghara, Robinette, Niezrecki"),
]



# ---------------------------------------------------------------- students and alumni (from the director's CV, Sept. 2026)
STUDENTS = [
    {"name": "Arash Rezaee", "photo": "arash", "status": "Ph.D. Candidate, joined 2022", "focus": "AI-driven resource allocation in optical networks; impairment-aware provisioning in multi-band, space-division multiplexed networks; spectral versus spatial capacity scaling; reproducible optical network benchmarking with FUSION.", "linkedin": ""},
    {"name": "Ryan McCann", "photo": "ryan", "status": "Ph.D. Student, joined 2024", "focus": "Co-founder and lead developer of FUSION, supported by MIT I-Corps and AT&T; reinforcement learning for software-defined elastic optical networks; failure-aware routing and realistic simulation of elastic optical and mesh networks.", "linkedin": ""},
    {"name": "Ken Patrick Watts", "photo": "ken", "status": "Ph.D. Student, joined 2022", "focus": "Scalable, real-time detection of cyber attacks on smart power grids with machine learning; adaptive transfer learning for day-zero network intrusion detection; the NATIG cyber-physical co-simulation testbed (HELICS, GridLAB-D, ns-3).", "linkedin": ""},
    {"name": "Suvhasis Mukhopadhyay", "photo": "suvhasis", "status": "Ph.D. Student, joined 2023", "focus": "Impact of individual physical layer impairments on elastic optical network performance; impairment-aware routing, spectrum, modulation, and power allocation; dynamic optical networking.", "linkedin": ""},
    {"name": "Mehran Sasaninia", "photo": "mehran", "status": "Ph.D. Student, joined 2023", "focus": "Federated learning to detect cyber attacks in the smart grid; smart false data injection attacks and anomaly detection in smart meters (IEEE SmartGridComm 2025); centralized versus federated learning for grid anomaly detection.", "linkedin": ""},
    {"name": "Ayush Pandey", "status": "Ph.D. Student, joined 2024", "focus": "Newest member of the group; smart grid cybersecurity and AI for cyber-physical systems.", "linkedin": ""},
]
ALUMNI_FEATURED = [
    {"name": "Md Zahidul Islam", "photo": "zahidul", "degree": "Ph.D. 2025", "role": "Assistant Professor", "org": "Southern Illinois University Carbondale", "focus": "Resilient PMU networking and cyber-physical restoration of power distribution systems. Primary advisor Yuzhang Lin.", "linkedin": ""},
    {"name": "Shamsun Nahar Edib", "photo": "shamsun", "degree": "Ph.D. 2024", "role": "Assistant Professor", "org": "Montana State University", "focus": "Cross-domain resilient sensing and communication architectures for power grid monitoring. Primary advisor Yuzhang Lin. Best Ph.D. Student Award.", "linkedin": ""},
]
ALUMNI_PHD = [
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
GIFT_URL = "https://securelb.imodules.com/s/1355/lowell/forms/forms.aspx?sid=1355&gid=4&pgid=893&cid=2172"

# Center social accounts. Paste the full profile URLs here; the "Follow SCyPS" links appear in the
# footer and the contact block only for entries that are filled in.
SOCIAL = {
    "linkedin": "",   # e.g. https://www.linkedin.com/company/<page-name>
    "x": "",          # e.g. https://x.com/<handle>
}
def social_links(cls="follow"):
    items = []
    if SOCIAL.get("linkedin"):
        items.append(f'<a href="{esc(SOCIAL["linkedin"])}" title="SCyPS on LinkedIn"><i class="fa-brands fa-linkedin" aria-hidden="true"></i><span>LinkedIn</span></a>')
    if SOCIAL.get("x"):
        items.append(f'<a href="{esc(SOCIAL["x"])}" title="SCyPS on X"><i class="fa-brands fa-x-twitter" aria-hidden="true"></i><span>X</span></a>')
    return f'<div class="{cls}"><span class="lbl">Follow SCyPS</span>{"".join(items)}</div>' if items else ""

def initials(name):
    return "".join(w[0] for w in name.replace("(", "").split() if w[0].isupper())[:2]
def stu_avatar(p):
    key = p.get("photo")
    if key and IMG.get("head_" + key):
        return f'<img class="avatar lg round" src="data:image/png;base64,{IMG["head_" + key]}" alt="{esc(p["name"])}" width="360" height="360">'
    return f'<span class="avatar mono lg round" aria-hidden="true">{esc(initials(p["name"]))}</span>'
def student_card(st):
    li = f'<a href="{esc(st["linkedin"])}">LinkedIn</a>' if st.get("linkedin") else ''
    return (f'<article class="stu">{stu_avatar(st)}'
            f'<h3>{esc(st["name"])}</h3><p class="ptitle">{esc(st["status"])}</p><p class="focus">{esc(st["focus"])}</p>'
            + (f'<p class="pmeta"><span class="mi">{li}</span></p>' if li else '') + '</article>')
def alum_feature(a):
    li = f'<span class="mi"><a href="{esc(a["linkedin"])}">LinkedIn</a></span>' if a.get("linkedin") else ''
    return (f'<article class="stu feat">{stu_avatar(a)}'
            f'<h3>{esc(a["name"])} <span class="ptag">{esc(a["degree"])}</span></h3><p class="ptitle"><b>{esc(a["role"])}</b>, {esc(a["org"])}</p>'
            f'<p class="focus">{esc(a["focus"])}</p>' + (f'<p class="pmeta">{li}</p>' if li else '') + '</article>')

# ---------------------------------------------------------------- sponsors
# Drop official logo files into a "logos" folder next to this script, named by key
# (nsf.svg, doe.png, redhat.svg ...). SVG, PNG, or JPG. Tiles fall back to a typeset name.
SPONSORS = {
    "Federal sponsors": [
        {"key": "nsf", "name": "U.S. National Science Foundation", "url": "https://www.nsf.gov", "note": "SUMMIT (MRI Track 2, Award #2511635) and CAREER awards"},
        {"key": "doe", "name": "U.S. Department of Energy", "url": "https://www.energy.gov", "note": "CyberCARE cybersecurity center for energy delivery"},
        {"key": "onr", "name": "Office of Naval Research", "url": "https://www.onr.navy.mil", "note": "Department of the Navy. Post-disaster restoration of cyber-physical distribution grids"},
        {"key": "army", "name": "U.S. Army", "url": "https://www.army.mil", "note": "ARPO autonomous robotic planning and optimization"},
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
<g class="grow"><rect x="136" y="70" width="40" height="58" rx="3" fill="#044978" opacity=".85" style="transform-origin:156px 128px"/></g>
<g class="grow" style="animation-delay:.6s"><rect x="182" y="52" width="44" height="76" rx="3" fill="#0A777F" style="transform-origin:204px 128px"/></g>
<g class="grow" style="animation-delay:1.2s"><rect x="232" y="82" width="44" height="46" rx="3" fill="#3BA995" style="transform-origin:254px 128px"/></g>
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
<g class="grow"><rect x="200" y="94" width="10" height="42" fill="#0A777F" style="transform-origin:205px 136px"/></g>
<g class="grow" style="animation-delay:.5s"><rect x="216" y="76" width="10" height="60" fill="#0A777F" style="transform-origin:221px 136px"/></g>
<g class="grow" style="animation-delay:1s"><rect x="232" y="106" width="10" height="30" fill="#0A777F" style="transform-origin:237px 136px"/></g>
<g class="grow" style="animation-delay:1.5s"><rect x="248" y="62" width="10" height="74" fill="#0A777F" style="transform-origin:253px 136px"/></g>
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
<path class="trace" d="M284 48h10l6-14 8 28 8-20 6 6h14" stroke="#3BA995" stroke-width="2"/>
<!-- data uplink from vehicles to the hospital and bridge -->
<path d="M120 58h108" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow" d="M120 58h108" stroke="#0A777F" stroke-width="2"/>
<circle cx="120" cy="58" r="4.5" fill="#0A777F"/><path d="M120 62v34" stroke="#D5DCE5" stroke-width="1.4"/><path class="flow slow" d="M120 62v34" stroke="#0A777F" stroke-width="2"/>
<text x="180" y="162" font-size="11" fill="#5B6B82" text-anchor="middle">connected roads, hospitals, and structures</text>
</svg>""",
}
ART = {k: theme_svg(v) for k, v in ART.items()}
SCHEMATIC = theme_svg(SCHEMATIC)

METRICS = {}
_mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json")
if os.path.exists(_mp):
    METRICS = json.load(open(_mp))
LIVE_METRICS = False   # True: also refresh the figures from OpenAlex in the visitor's browser (needs internet on the page)

def metrics_slot(p):
    if p.get("inst", "Lowell") is None: return ""
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
    lines += [f'<h3>{esc(p["name"])}{tag}</h3>', f'<p class="ptitle">{esc(p["title"])}</p>', f'<p class="pareas">{esc(p["areas"])}</p>']
    if p.get("role"):
        lines.append(f'<p class="prole">{esc(p["role"])}</p>')
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(f'<span>{esc(p["phone"])}</span>')
    if p.get("office"): meta.append(f'<span>{esc(p["office"])}</span>')
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">{"NYU profile" if "nyu.edu" in p["url"] else ("LinkedIn" if "linkedin.com" in p["url"] else "UMass Lowell profile")}</a>')
    lines.append('<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in meta) + '</p>')
    lines.append(metrics_slot(p))
    return '<article class="person">' + "".join(lines) + '</article>'

def person_row(p):
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(esc(p["phone"]))
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">{"LinkedIn" if "linkedin.com" in p["url"] else "Profile"}</a>')
    tag = f'<span class="ptag">{esc(p["tag"])}</span>' if p.get("tag") else ''
    return ('<li class="prow">' + avatar(p, "sm") + '<div><span class="pname">' + esc(p["name"]) + tag + '</span><span class="ptitle2">' + esc(p["title"]) + '</span>'
            '<span class="pareas2">' + esc(p["areas"]) + '</span><div class="pcontact">' + '<span class="sep"></span>'.join(meta) + '</div>' + metrics_slot(p) + '</div></li>')

# ---------------------------------------------------------------- counts
n_pubs = len(P)
n_journal = sum(1 for p in P if p["type"] == "journal")
n_faculty = 1 + len(FACULTY["core"]) + len(FACULTY["affiliated"])

def build():
    thrusts_html = "".join(
        f'<div class="thrust"><div class="art">{ART[i]}</div><div class="body"><h3>{esc(t)}</h3><p>{esc(d)}</p><div class="who">{esc(w)}</div></div></div>'
        for i, t, d, w in THRUSTS)

    projects_html = ""
    for pr in PROJECTS:
        tagcls = "tag new" if pr["tag"].startswith("New") else "tag"
        share = f'<small>{esc(pr["share"])}</small>' if pr.get("share") else ''
        amt = f'<div class="amt">{esc(pr["amount"])}{share}<small>{esc(pr["period"])}</small></div>' if pr["amount"] else f'<div class="amt"><small>{esc(pr["period"])}</small></div>'
        projects_html += (f'<div class="proj"><div class="when"><span class="{tagcls}">{esc(pr["tag"])}</span><br>{esc(pr["domain"])}</div>'
                          f'<div><h3>{esc(pr["title"])}</h3><div class="sponsor">{esc(pr["sponsor"])}</div>'
                          f'<p class="desc">{esc(pr["desc"])}</p><p class="team">{esc(pr["team"])}</p></div>{amt}</div>')

    tools_html = "".join(f'<div class="tool"><h4>{esc(t["name"])}</h4><p>{esc(t["what"])}</p></div>' for t in TOOLS)

    d = FACULTY["director"]
    director_html = ('<div class="director">' + avatar(d, "xl") + '<div>' + person_card(d, with_photo=False) +
                     f'<div class="bio"><p>{esc(d["bio"])}</p></div></div></div>')
    core_html = '<div class="core">' + "".join(person_card(p, "lg") for p in FACULTY["core"]) + '</div>'
    aff_html = '<ul class="plist">' + "".join(person_row(p) for p in FACULTY["affiliated"]) + '</ul>'
    ext_html = '<ul class="plist">' + "".join(person_row(p) for p in FACULTY["external"]) + '</ul>'
    students_html = "".join(student_card(st) for st in STUDENTS)
    lablife_html = "".join(f'<img src="data:image/jpeg;base64,{IMG[f"lab{i}"]}" alt="Members of the Advanced Communication Networks Laboratory" width="760" height="406">' for i in range(1, 7) if IMG.get(f"lab{i}"))
    alumni_feat_html = "".join(alum_feature(a) for a in ALUMNI_FEATURED)
    alumni_phd_html = "".join(f'<li><span class="yr">{esc(y)}</span><span><b>{esc(n)}</b>{(" <span class=\"where\">" + esc(w) + "</span>") if w else ""}</span></li>' for y, n, w in ALUMNI_PHD)
    alumni_pd_html = "".join(f'<li><span><b>{esc(n)}</b>{(" <span class=\"where\">" + esc(w) + "</span>") if w else ""}</span></li>' for n, w in ALUMNI_POSTDOC)
    sponsors_html = "".join(
        f'<div class="sgroup"><h3>{esc(group)}</h3><div class="logos">' + "".join(logo_tile(sp) for sp in items) + '</div></div>'
        for group, items in SPONSORS.items())

    news_html = "".join(f'<li><time>{esc(w)}</time><p>{esc(t)}</p></li>' for w, t in NEWS)

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
            out += (f'<li data-year="{p["year"]}" data-type="{p["type"]}" data-fac="{" ".join(p["faculty"])}">'
                    f'<div><div class="a">{fmt_authors(p["authors"])}</div>{title}'
                    f'<div class="v"><i>{esc(p["venue"])}</i>, {esc(p["details"])}</div></div><div class="side">{side}</div></li>')
        if cur is not None: out += "</ul>"
        return out
    pubs_html = render_pubs(P)

    facts = [
        ("$2M", "NSF MRI Track 2 award for the SUMMIT federated smart grid testbed, 2026 to 2029"),
        (str(n_faculty), "affiliated faculty across engineering, computing, and medicine"),
        (str(n_pubs), f"peer-reviewed papers since 2021, {n_journal} of them in journals"),
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

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Center for Smart Cyber-Physical Systems (SCyPS) | UMass Lowell</title>
<meta name="description" content="UMass Lowell's Center for Smart Cyber-Physical Systems researches secure, resilient, and intelligent systems for energy, transportation, and healthcare: smart grid cybersecurity, optical and 6G networks, fault-tolerant edge computing, hardware security, and AI for cyber-physical control.">
<meta property="og:title" content="Center for Smart Cyber-Physical Systems (SCyPS) | UMass Lowell">
<meta property="og:description" content="Research, people, funded projects, and publications from UMass Lowell's Center for Smart Cyber-Physical Systems.">
<meta property="og:type" content="website">
<link rel="icon" type="image/png" href="{img_src("favicon")}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
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
      <li><a href="#sponsors">Sponsors</a></li>
      <li><a href="#people">People</a></li>
      <li><a href="#students">Students</a></li>
      <li><a href="#alumni">Alumni</a></li>
      <li><a href="#publications">Publications</a></li>
      <li><a href="#news">News</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <a class="gift" href="{GIFT_URL}">Make a Gift</a>
    <button class="theme" id="theme" type="button" aria-label="Switch to dark mode"><svg class="moon" viewBox="0 0 24 24"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></svg><span class="lbl">Dark</span></button>
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
    <div class="about-grid">
      <div>
        <h3>Mission</h3>
        <p>The mission of the Center for Smart Cyber-Physical Systems (SCyPS) is to develop high-impact solutions to key challenges in heterogeneous distributed cyber-physical systems that support emerging smart society, data-centric applications. By taking an interdisciplinary approach with a team of science and engineering researchers, SCyPS commits to increasing cyber-physical system reliability and scalability, improving resource utilization, and guaranteeing system security and privacy. SCyPS will engage industry and community partners to meet their needs while training students and building the future workforce.</p>
        <h3 style="margin-top:22px">Vision</h3>
        <p>The Center for Smart Cyber-Physical Systems (SCyPS) will establish itself as an internationally recognized center for research and education focused on innovation, evaluation, and optimization of hardware and software technologies for an advanced, smart society.</p>
        <div class="domains"><span>Energy and power</span><span>Transportation</span><span>Healthcare</span></div>
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
    <div class="shead"><h2>Research thrusts</h2><p>Six connected lines of work. Most projects cut across two or three of them, which is the point of running them under one roof.</p></div>
    <div class="thrusts">{thrusts_html}</div>
  </div>
</section>

<section id="projects">
  <div class="wrap">
    <div class="shead"><h2>Funded projects</h2><p>Sponsored research led by center faculty since the center was founded in 2021, current awards first. Three new awards started in 2026, headed by the NSF MRI SUMMIT testbed.</p></div>
    <div class="feature">
      <div class="copy">
        <span class="kicker">New in 2026</span>
        <h3>SUMMIT: a three-site smart grid testbed you can attack, defend, and restore</h3>
        <p>NSF's Major Research Instrumentation program is funding a federated cyber-physical instrument that links real-time power system simulation, grid communication networks, and control and cybersecurity hardware across UMass Lowell, NYU, and West Virginia University. RTDS real-time digital simulators run high-fidelity models of the Northeast's backbone transmission grid fast enough to drive real controllers and network hardware in the loop, and a wide-area software-defined network ties the three sites together over the Internet. Researchers at any site will be able to run attack, defense, and restoration experiments on the shared testbed, and students will train on the same equipment utilities and vendors use.</p>
        <div class="meta">
          <div><b>$2.0M</b><span>NSF MRI Track 2, Award #2511635</span></div>
          <div><b>Oct 2026 to Sep 2029</b><span>award period</span></div>
          <div><b>Vinod Vokkarane, PI</b><span>Co-PIs Orlando Arias, Lewis Tseng, Yuzhang Lin</span></div>
          <div><b>Postdoc search open</b><span>postdoctoral research associate, Fall 2026</span></div>
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
      </div>
      <figure class="arch">
        <img src="{img_src("summit_arch")}" alt="SUMMIT architecture: at the UMass Lowell main site, signal generator, power amplifier, grid simulator, network emulator, and optical, RF, and FPGA equipment connect to an RTDS real-time digital simulator and a control and monitoring workstation through a core network switch; a wide-area network over the Internet links the WVU and NYU sites, each with its own switch, controller, and simulator" width="1800" height="748">
        <figcaption>SUMMIT architecture: the UMass Lowell main site, the wide-area software-defined network, and the WVU and NYU federation sites</figcaption>
      </figure>
    </div>
    <div class="ledger">{projects_html}</div>
    <div class="tools">{tools_html}</div>
  </div>
</section>

<section id="sponsors">
  <div class="wrap">
    <div class="shead"><h2>Sponsors and partners</h2><p>The agencies, companies, and institutions behind the center's current research.</p></div>
    {sponsors_html}
    <div class="ack">
      <p>This material is based upon work supported by the U.S. National Science Foundation under Grant No. 2511635. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.</p>
      <p>Research at the center is also supported by the U.S. Department of Energy, the Office of Naval Research, the U.S. Army, the Commonwealth of Massachusetts, the International Atomic Energy Agency, the Massachusetts Technology Collaborative, Red Hat, and Navia Energy.</p>
    </div>
  </div>
</section>

<section id="people" class="tint">
  <div class="wrap">
    <div class="shead"><h2>People</h2><p>Faculty from the Francis College of Engineering and the Kennedy College of Sciences, plus long-running collaborators at partner universities and companies. Citation counts and h-index are shown with their source; figures from different indexes are not directly comparable.</p></div>
    {director_html}
    {core_html}
    <div class="group"><h3>Affiliated researchers</h3><p>UMass Lowell faculty who collaborate on center projects and proposals.</p>{aff_html}</div>
    <div class="group"><h3>External collaborators</h3><p>Partners at other universities and companies who work with the center on current projects.</p>{ext_html}</div>
  </div>
</section>

<section id="students">
  <div class="wrap">
    <div class="shead"><h2>Students</h2><p>Doctoral students in the director's group, the Advanced Communication Networks Laboratory, working on center projects.</p></div>
    <div class="stugrid">{students_html}</div>
    <div class="lablife">
      <h3>Lab life</h3>
      <p>The Advanced Communication Networks Laboratory through the years.</p>
      <div class="labgrid">{lablife_html}</div>
    </div>
  </div>
</section>

<section id="alumni" class="tint">
  <div class="wrap">
    <div class="shead"><h2>Alumni</h2><p>Where the group's Ph.D. graduates and postdoctoral researchers have gone.</p></div>
    <div class="stugrid two">{alumni_feat_html}</div>
    <div class="alumcols">
      <div><h3>Ph.D. graduates</h3><ul class="alumlist">{alumni_phd_html}</ul></div>
      <div><h3>Postdoctoral alumni</h3><ul class="alumlist nodate">{alumni_pd_html}</ul>
      </div>
    </div>
  </div>
</section>

<section id="publications">
  <div class="wrap">
    <div class="shead"><h2>Publications</h2><p>Peer-reviewed journal papers, conference papers, and book chapters from center faculty since the center was founded in 2021, with links to the publisher's record. Center faculty are shown in bold; a paper with several center authors appears once.</p></div>
    <div class="filters" role="group" aria-label="Filter publications">
      <div class="fgroup"><span class="lab">Faculty</span>
        <button class="chip" data-f="fac" data-v="all" aria-pressed="true">All</button>
        <button class="chip" data-f="fac" data-v="Vokkarane" aria-pressed="false">Vokkarane</button>
        <button class="chip" data-f="fac" data-v="Arias" aria-pressed="false">Arias</button>
        <button class="chip" data-f="fac" data-v="Tseng" aria-pressed="false">Tseng</button>
        <button class="chip" data-f="fac" data-v="Son" aria-pressed="false">Son</button>
        <button class="chip" data-f="fac" data-v="Aghara" aria-pressed="false">Aghara</button>
        <button class="chip" data-f="fac" data-v="Lin" aria-pressed="false">Lin</button>
        <button class="chip" data-f="fac" data-v="Luo" aria-pressed="false">Luo</button>
        <button class="chip" data-f="fac" data-v="Xie" aria-pressed="false">Xie</button>
        <button class="chip" data-f="fac" data-v="Chigan" aria-pressed="false">Chigan</button>
        <button class="chip" data-f="fac" data-v="Inalpolat" aria-pressed="false">Inalpolat</button>
        <button class="chip" data-f="fac" data-v="Robinette" aria-pressed="false">Robinette</button>
        <button class="chip" data-f="fac" data-v="Yu" aria-pressed="false">Yu</button>
        <button class="chip" data-f="fac" data-v="Akyurtlu" aria-pressed="false">Akyurtlu</button>
        <button class="chip" data-f="fac" data-v="Niezrecki" aria-pressed="false">Niezrecki</button>
        <button class="chip" data-f="fac" data-v="Ranasingha" aria-pressed="false">Ranasingha</button>
      </div>
      <div class="fgroup"><span class="lab">Year</span>
        <button class="chip" data-f="year" data-v="all" aria-pressed="true">All</button>
        <button class="chip" data-f="year" data-v="2026" aria-pressed="false">2026</button>
        <button class="chip" data-f="year" data-v="2025" aria-pressed="false">2025</button>
        <button class="chip" data-f="year" data-v="2024" aria-pressed="false">2024</button>
        <button class="chip" data-f="year" data-v="2023" aria-pressed="false">2023</button>
        <button class="chip" data-f="year" data-v="2022" aria-pressed="false">2022</button>
        <button class="chip" data-f="year" data-v="2021" aria-pressed="false">2021</button>
      </div>
      <div class="fgroup"><span class="lab">Type</span>
        <button class="chip" data-f="type" data-v="all" aria-pressed="true">All</button>
        <button class="chip" data-f="type" data-v="journal" aria-pressed="false">Journal</button>
        <button class="chip" data-f="type" data-v="conference" aria-pressed="false">Conference</button>
        <button class="chip" data-f="type" data-v="chapter" aria-pressed="false">Chapter</button>
      </div>
      <div class="search"><label for="q" class="lab">Search</label><input id="q" type="search" placeholder="title, author, or venue" autocomplete="off"></div>
    </div>
    <div class="count" id="count" aria-live="polite">Showing {n_pubs} of {n_pubs} papers</div>
    <div id="publist">{pubs_html}</div>
    <p class="pubnote">Records verified against Crossref (the NSDI paper is listed from the USENIX program). Venues that do not register DOIs, such as ANS Transactions and INMM proceedings, are not captured, and for faculty with common names only papers with a confirmed UMass Lowell affiliation are included. Send corrections or additions to SCyPS@uml.edu.</p>
  </div>
</section>

<section id="news" class="tint">
  <div class="wrap">
    <div class="shead"><h2>News</h2><p>Awards, papers, and milestones from the last eighteen months.</p></div>
    <ul class="timeline">{news_html}</ul>
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
          <p>Ph.D. and M.S. students in the center work on real instruments and real data: the federated smart grid testbed, multi-band optical network simulation, fault-tolerant edge systems, and hardware security. A postdoctoral research associate position on SUMMIT is open in Fall 2026. Prospective students should write to a faculty member whose work matches their interests and copy SCyPS@uml.edu.</p>
        </div>
        <div class="block">
          <h3>Industry and agency partners</h3>
          <ul>
            <li>Run attack, defense, and restoration experiments on the SUMMIT testbed once it opens to collaborators.</li>
            <li>Sponsor targeted research and gain early access to results and open-source tools such as FUSION.</li>
            <li>Recruit co-ops, interns, and graduates trained on cyber-physical infrastructure.</li>
            <li>Join proposals to NSF, DOE, DoD, and state programs as a partner site or end user.</li>
          </ul>
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

<footer id="contact" class="uml-footer" role="contentinfo">
  <div class="wrap">
    <div class="cols">
      <div class="col">
        <div class="flogo"><img src="{img_src("logo_name")}" alt="SCyPS, Center for Smart Cyber-Physical Systems" width="594" height="453"></div>
        <a href="https://www.uml.edu/" title="UMass Lowell home">{UML_LOGO}</a>
        <address><strong>Center for Smart Cyber-Physical Systems (SCyPS)</strong><br>UMass Lowell<br>1 University Ave. Lowell, MA 01854<br>Email: <a href="mailto:SCyPS@uml.edu">SCyPS@uml.edu</a></address>
        {social_links("follow")}
      </div>
      <div class="col menu">
        <nav aria-label="Footer menu"><h2>Menu</h2>
          <ul><li><a href="#about">About</a></li><li><a href="#research">Research</a></li><li><a href="#projects">Projects</a></li><li><a href="#sponsors">Sponsors</a></li><li><a href="#people">People</a></li><li><a href="#students">Students</a></li><li><a href="#alumni">Alumni</a></li><li><a href="#publications">Publications</a></li><li><a href="#news">News</a></li><li><a href="{GIFT_URL}">Make a Gift</a></li></ul>
        </nav>
      </div>
      <div class="col dir">
        <h2>Director</h2>
        <p>Vinod M. Vokkarane<br>Ball Hall 409, North Campus<br><a href="mailto:vinod_vokkarane@uml.edu">vinod_vokkarane@uml.edu</a><br>978-934-3345</p>
      </div>
      <div class="col social">
        <ul>
          <li><a href="https://www.tiktok.com/@umass_lowell" title="Find us on TikTok"><i class="fa-brands fa-tiktok" aria-hidden="true"></i><span class="label">Find us on TikTok</span></a></li>
          <li><a href="https://www.facebook.com/umlowell" title="Find us on Facebook"><i class="fa-brands fa-facebook" aria-hidden="true"></i><span class="label">Find us on Facebook</span></a></li>
          <li><a href="https://twitter.com/umasslowell" title="Follow us on X"><i class="fa-brands fa-x-twitter" aria-hidden="true"></i><span class="label">Follow us on X</span></a></li>
          <li><a href="https://www.youtube.com/user/umasslowell" title="Watch us on YouTube"><i class="fa-brands fa-youtube" aria-hidden="true"></i><span class="label">Watch us on YouTube</span></a></li>
          <li><a href="https://instagram.com/umasslowell" title="Find us on Instagram"><i class="fa-brands fa-instagram" aria-hidden="true"></i><span class="label">Find us on Instagram</span></a></li>
          <li><a href="https://www.linkedin.com/school/university-of-massachusetts-lowell/" title="Find us on LinkedIn"><i class="fa-brands fa-linkedin" aria-hidden="true"></i><span class="label">Find us on LinkedIn</span></a></li>
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
      <p class="fine">Updated September 2026. Grant figures are total awards as reported by sponsors; the UMass Lowell share is noted where a project is a multi-institution consortium. Photographs courtesy of UMass Lowell.</p>
    </div>
  </div>
</footer>

<script>
(function(){{
  var root=document.documentElement, tb=document.getElementById('theme');
  function effective(){{ var t=root.getAttribute('data-theme'); if(t) return t; return (window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light'; }}
  function paintToggle(){{ var d=effective()==='dark'; tb.setAttribute('aria-label', d?'Switch to light mode':'Switch to dark mode'); tb.querySelector('.lbl').textContent=d?'Light':'Dark'; }}
  tb.addEventListener('click',function(){{ var next=effective()==='dark'?'light':'dark'; root.setAttribute('data-theme',next); try{{localStorage.setItem('scyps-theme',next);}}catch(e){{}} paintToggle(); }});
  paintToggle();
  var tg=document.querySelector('.navtoggle'),menu=document.getElementById('menu');
  window.addEventListener('load',function(){{ var ic=document.querySelector('.uml-footer .fa-brands'); if(ic){{ var ff=getComputedStyle(ic).fontFamily||''; if(ff.indexOf('Font Awesome')<0) document.querySelector('.uml-footer').classList.add('no-fa'); }} }});
  tg.addEventListener('click',function(){{var o=menu.classList.toggle('open');tg.setAttribute('aria-expanded',o);}});
  menu.addEventListener('click',function(e){{if(e.target.tagName==='A'){{menu.classList.remove('open');tg.setAttribute('aria-expanded','false');}}}});

  var links=[].slice.call(document.querySelectorAll('.links a'));
  var secs=links.map(function(a){{return document.querySelector(a.getAttribute('href'));}}).filter(Boolean);
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
    count.textContent='Showing '+shown+' of '+total+' papers'+(shown?'':'. Nothing matches these filters; clear one to see more.');
  }}
  document.querySelectorAll('.chip').forEach(function(b){{
    b.addEventListener('click',function(){{
      var f=b.getAttribute('data-f');
      document.querySelectorAll('.chip[data-f="'+f+'"]').forEach(function(x){{x.setAttribute('aria-pressed','false');}});
      b.setAttribute('aria-pressed','true'); state[f]=b.getAttribute('data-v'); apply();
    }});
  }});
  document.getElementById('q').addEventListener('input',function(e){{state.q=e.target.value;apply();}});

  // live citation metrics from OpenAlex (name + institution match; cached per browser for 7 days)
  (function(){{
    var els=[].slice.call(document.querySelectorAll('.metrics[data-name]')); if(!els.length) return;
    var KEY='scyps-metrics-v1', TTL=7*864e5, cache={{}};
    try{{cache=JSON.parse(localStorage.getItem(KEY)||'{{}}')||{{}};}}catch(e){{cache={{}};}}
    function fmt(n){{return (n||0).toLocaleString();}}
    function render(el,m){{el.innerHTML='<span><b>'+fmt(m.c)+'</b> citations</span><span><b>'+m.h+'</b> h-index</span><span><b>'+fmt(m.w)+'</b> works</span><span class="src">OpenAlex</span>';}}
    els.forEach(function(el,i){{
      var name=el.getAttribute('data-name'), inst=el.getAttribute('data-inst')||'Lowell', k=name+'|'+inst;
      if(cache[k]&&(Date.now()-cache[k].t)<TTL){{render(el,cache[k]);return;}}
      setTimeout(function(){{
        fetch('https://api.openalex.org/authors?search='+encodeURIComponent(name)+'&per_page=10&mailto=SCyPS@uml.edu')
          .then(function(r){{return r.json();}})
          .then(function(d){{
            var res=d.results||[];
            var pick=null;
            for(var j=0;j<res.length;j++){{
              var a=res[j], insts=(a.last_known_institutions||[]).concat((a.affiliations||[]).map(function(x){{return x.institution||{{}};}}));
              if(JSON.stringify(insts).indexOf(inst)>-1){{pick=a;break;}}
            }}
            if(!pick){{el.innerHTML='';return;}}
            var m={{c:pick.cited_by_count||0,h:(pick.summary_stats||{{}}).h_index||0,w:pick.works_count||0,t:Date.now()}};
            cache[k]=m; try{{localStorage.setItem(KEY,JSON.stringify(cache));}}catch(e){{}}
            render(el,m);
          }}).catch(function(){{el.innerHTML='';}});
      }}, i*120);
    }});
  }})();
}})();
</script>
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT}: {len(page)/1024:.0f} KB; {n_pubs} pubs ({n_journal} journal); {n_faculty} faculty; {len(IMG)} images embedded")

if __name__ == "__main__":
    build()
