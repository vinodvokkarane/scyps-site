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
CORE = {"Vokkarane", "Arias", "Tseng", "Son"}

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
        {"name": "Lewis Tseng", "photo": "tseng", "title": "Associate Professor, Electrical and Computer Engineering",
         "areas": "High-performance fault-tolerant distributed systems, blockchain-based systems, intelligent traffic and vehicular computing",
         "email": "Lewis_Tseng@uml.edu", "phone": "", "office": "Ball Hall, 3rd floor",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/tseng-lewis.aspx",
         "role": "NSF CAREER awardee (2023) on fault-tolerant edge computing for cyber-physical systems under cyber attack; Co-PI on SUMMIT. Joined UMass Lowell in 2024 after Clark University, Boston College, and Toyota InfoTechnology Center."},
        {"name": "Seung Woo Son", "photo": "son", "title": "Associate Professor, Electrical and Computer Engineering",
         "areas": "High performance computing, parallel I/O and data-intensive computing, compiler optimizations, embedded systems",
         "email": "SeungWoo_Son@uml.edu", "phone": "978-934-6846", "office": "Ball Hall 419",
         "url": "https://www.uml.edu/engineering/electrical-computer/faculty/son-seung-woo.aspx",
         "role": "NSF CAREER awardee (2018); brings HPC, silent-data-corruption detection, and on-device stream analytics to the center's data-intensive CPS work."},
    ],
    "board": [
        {"name": "Jomol Mathew", "title": "Chief Research Informatics Officer, UMass Chan Medical School",
         "areas": "Research informatics, digital health", "email": "Jomol.Mathew@umassmed.edu", "phone": ""},
        {"name": "Yan Luo", "photo": "luo", "title": "Professor, Electrical and Computer Engineering; Robotics",
         "areas": "Computer architecture, network systems", "email": "yan_luo@uml.edu", "phone": "978-934-2592"},
        {"name": "Yuanchang Xie", "photo": "xie", "title": "Professor, Civil and Environmental Engineering",
         "areas": "Transportation engineering, smart and connected transportation", "email": "Yuanchang_Xie@uml.edu", "phone": "978-934-3681"},
        {"name": "Sukesh Aghara", "photo": "aghara", "title": "Professor, Chemical (Nuclear) Engineering; Associate Dean of Graduate Studies and Research",
         "areas": "Nuclear nonproliferation, nuclear security and safeguards, nuclear energy for decarbonization", "email": "Sukesh_Aghara@uml.edu", "phone": "978-934-3115"},
    ],
    "affiliated": [
        {"name": "Yu Cao", "photo": "cao", "title": "Professor, Miner School of Computer and Information Sciences; Director, UMass Center for Digital Health",
         "areas": "Medical imaging, multimodal deep learning, computer vision, AI, digital health", "email": "yu_cao@uml.edu", "phone": "978-934-3628"},
        {"name": "Chunxiao (Tricia) Chigan", "photo": "chigan", "title": "Professor, Electrical and Computer Engineering",
         "areas": "Communication networks and network security", "email": "Tricia_Chigan@uml.edu", "phone": "978-934-3364"},
        {"name": "Murat Inalpolat", "photo": "inalpolat", "title": "Professor, Mechanical and Industrial Engineering; Associate Chair for Doctoral Studies",
         "areas": "Structural health monitoring, diagnostics and prognostics, structural dynamics, vibrations, acoustics, signal processing", "email": "Murat_Inalpolat@uml.edu", "phone": "978-934-2556"},
        {"name": "Paul Robinette", "photo": "robinette", "title": "Associate Professor, Electrical and Computer Engineering; Associate Chair for M.S. Programs",
         "areas": "Robotics, human-robot interaction; Printed Electronics Research Collaborative; Raytheon UMass Lowell Research Institute", "email": "Paul_Robinette@uml.edu", "phone": "978-934-3347"},
        {"name": "Hengyong Yu", "photo": "yu", "title": "Professor, Electrical and Computer Engineering",
         "areas": "Biomedical imaging, medical image reconstruction, image processing and analysis", "email": "Hengyong_Yu@uml.edu", "phone": "978-934-6756"},
    ],
    "collaborators": [
        {"name": "Yuzhang Lin", "org": "NYU Tandon School of Engineering", "note": "Co-PI, SUMMIT and ONR restoration project; six years of joint smart grid research with the center"},
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
     "desc": ("A federated cyber-physical testbed that links real-time power system simulation, grid communication "
              "networks, and protection and control devices across three universities, so researchers can run "
              "attack, defense, and restoration experiments on a shared instrument. A postdoctoral researcher will "
              "lead federation development."),
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
    {"tag": "Active", "sponsor": "Office of Naval Research",
     "title": "Unified Post-Disaster Restoration Planning for Cyber-Physical Power Distribution Systems",
     "amount": "$550K", "period": "Jan 2024 to Dec 2026",
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
    {"tag": "Active", "sponsor": "National Science Foundation, CAREER",
     "title": "Towards Fault-tolerant Edge Computing for Cyber-Physical Systems: Distributed Primitives for Coordination under Cyber Attacks",
     "amount": "About $500K", "period": "2023 onward",
     "team": "PI Lewis Tseng",
     "desc": "Coordination primitives that let edge computing systems keep working when some nodes are faulty or compromised.",
     "domain": "Edge"},
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
    {"name": "SUMMIT (in development)", "what": "Three-site federated smart grid testbed funded by the NSF MRI award, opening in 2026-2027 to collaborators for attack, defense, and restoration experiments."},
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
    "10.1109/TIA.2025.3625866", "journal", ["Vokkarane"], "Smart grid")
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

# --- 2025
pub(2025, ["M. Z. Islam","Y. Lin","V. M. Vokkarane"],
    "Cyber Security Constrained Economic Dispatch for Resilient Power System Operation",
    "IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)", "pp. 1-6, Sept. 2025",
    "10.1109/SmartGridComm65349.2025.11204587", "conference", ["Vokkarane"], "Smart grid")
pub(2025, ["M. Sasaninia","V. M. Vokkarane","Y. Lin","O. Arias"],
    "Exploring a Smart FDI Attack and Enhancing Anomaly Detection in Smart Meters",
    "IEEE International Conference on Communications, Control, and Computing Technologies for Smart Grids (SmartGridComm)", "pp. 1-6, Sept. 2025",
    "10.1109/SmartGridComm65349.2025.11204616", "conference", ["Vokkarane","Arias"], "Smart grid")
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
    "10.1109/TPWRS.2024.3387338", "journal", ["Vokkarane"], "Smart grid")
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
    ("Mar 2026", "The U.S. Army ARPO project on autonomous robotic planning and optimization begins ($225K)."),
    ("Dec 2025", "Two GLOBECOM 2025 papers from the Tseng group: satellite-edge-enabled multi-drone search and content-aware gossip for mobile device clouds."),
    ("Sep 2025", "Two SmartGridComm 2025 papers: cyber-security-constrained economic dispatch, and smart false-data-injection attacks on smart meters with Orlando Arias and Yuzhang Lin; plus a joint ECOC 2025 paper on planning ultra-high-capacity multi-band SDM networks."),
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
        fam = a.split()[-1]
        if fam in CORE and (fam != "Son" or a.startswith("S. W.")):
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
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">UMass Lowell profile</a>')
    lines.append('<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in meta) + '</p>')
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
n_faculty = 1 + len(FACULTY["core"]) + len(FACULTY["board"]) + len(FACULTY["affiliated"])
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
  --line:#D5DCE5; --line-2:#E8EDF2; --signal:#0E8FA3; --signal-2:#0B7385; --signal-tint:#E3F3F6;
  --amber:#E39A16; --amber-2:#FBEFD3; --amber-text:#7A4E00;
  --navy:#0E2036; --navy-2:#09162A; --on-navy:#FFFFFF; --on-navy-2:#C9D3E0; --on-navy-3:#9AA9BC;
  --journal-bg:#DCEFF3; --journal-fg:#0B5A69; --shadow:rgba(14,32,54,.35); --nav-bg:rgba(255,255,255,.9);
  --grid-line:rgba(14,32,54,.07); --illus-bg:#EEF4F8; --illus-bg-2:#E2EDF4;
  --max:1180px; --gutter:clamp(18px,4vw,48px); --fs-0:clamp(15px,1.05vw,17px); --radius:12px;
}
:root[data-theme="dark"]{
  --bg:#0B1729; --bg-2:#0F1E33; --surface:#142640; --ink:#E8EEF5; --ink-2:#C2CDDB; --ink-3:#92A1B5;
  --line:#24384F; --line-2:#1B2D45; --signal:#3FC1D6; --signal-2:#5FD0E2; --signal-tint:#123645;
  --amber:#E9A83A; --amber-2:#3B2C0E; --amber-text:#F5C766;
  --navy:#08111F; --navy-2:#060C17; --journal-bg:#123645; --journal-fg:#7ADCEB; --shadow:rgba(0,0,0,.6);
  --nav-bg:rgba(11,23,41,.86); --grid-line:rgba(232,238,245,.06); --illus-bg:#0F2238; --illus-bg-2:#16304C;
  color-scheme:dark;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0B1729; --bg-2:#0F1E33; --surface:#142640; --ink:#E8EEF5; --ink-2:#C2CDDB; --ink-3:#92A1B5;
    --line:#24384F; --line-2:#1B2D45; --signal:#3FC1D6; --signal-2:#5FD0E2; --signal-tint:#123645;
    --amber:#E9A83A; --amber-2:#3B2C0E; --amber-text:#F5C766;
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
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:66px;gap:16px}
.brand{display:flex;align-items:center;gap:12px;color:var(--ink);font-family:"Fraunces",Georgia,serif;font-size:19px;font-weight:600;letter-spacing:-.01em;min-width:0}
.brand span{white-space:nowrap}
.brand small{display:block;font-family:"IBM Plex Sans",Arial,sans-serif;font-weight:400;font-size:12px;color:var(--ink-3);letter-spacing:0}
.brand svg{width:34px;height:34px;flex:none}
.brand .lg-bg{fill:var(--ink)} .brand .lg-dot{fill:var(--bg)} .brand .lg-line{stroke:var(--bg)}
.navright{display:flex;align-items:center;gap:8px}
.links{display:flex;gap:2px;list-style:none;margin:0;padding:0}
.links a{display:block;padding:8px 12px;color:var(--ink-2);font-size:14.5px;border-radius:6px}
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
@media (max-width:600px){.brand small{display:none}.theme .lbl{display:none}.theme{padding:7px 8px}}
@media (max-width:920px){
  .links{display:none;position:absolute;left:0;right:0;top:66px;background:var(--bg);border-bottom:1px solid var(--line);flex-direction:column;padding:8px var(--gutter) 14px}
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
.shead h2::before{content:"";position:absolute;left:0;top:0;width:44px;height:3px;background:var(--signal);border-radius:2px}
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
.loop{margin-top:clamp(40px,5vw,64px);display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,.65fr);gap:clamp(20px,4vw,56px);align-items:center}
.schem{margin:0;border:1px solid var(--line);border-radius:var(--radius);color:var(--ink);background:
  linear-gradient(var(--grid-line) 1px,transparent 1px) 0 0/24px 24px,
  linear-gradient(90deg,var(--grid-line) 1px,transparent 1px) 0 0/24px 24px,var(--surface);padding:16px;box-shadow:0 12px 40px -28px var(--shadow)}
.schem svg{width:100%;height:auto;display:block}
.schem .s-ink{stroke:var(--ink)} .schem .f-ink{fill:var(--ink)} .schem .f-surface{fill:var(--surface)} .schem .f-muted{fill:var(--ink-3)} .schem .f-ink2{fill:var(--ink-2)}
.schem .s-sig{stroke:var(--signal)} .schem .f-amb{fill:var(--amber)} .schem .s-amb{stroke:var(--amber)}
.loop .txt h3{margin-bottom:10px}
.loop .txt p{color:var(--ink-2);font-size:15.5px}
@media (max-width:900px){.loop{grid-template-columns:1fr}}
.flow{stroke-dasharray:3 9;animation:flow 2.6s linear infinite}
.flow.slow{animation-duration:4.2s}
@keyframes flow{to{stroke-dashoffset:-48}}
.pulse{animation:pulse 3s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
@media (prefers-reduced-motion:reduce){.flow,.pulse{animation:none}.flow{stroke-dasharray:none}}

/* research */
.thrusts{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.thrust{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
.thrust .art{aspect-ratio:2/1;background:linear-gradient(160deg,var(--illus-bg),var(--illus-bg-2));color:var(--ink);border-bottom:1px solid var(--line)}
.thrust .art svg{width:100%;height:100%;display:block}
.thrust .art .s-ink{stroke:var(--ink)} .thrust .art .f-ink{fill:var(--ink)} .thrust .art .f-surface{fill:var(--surface)} .thrust .art .f-muted{fill:var(--ink-3)}
.thrust .art .s-sig{stroke:var(--signal)} .thrust .art .f-sig{fill:var(--signal)} .thrust .art .f-sigt{fill:var(--signal-tint)} .thrust .art .f-amb{fill:var(--amber)} .thrust .art .s-amb{stroke:var(--amber)} .thrust .art .s-muted{stroke:var(--ink-3)}
.thrust .body{padding:22px 24px 24px;display:flex;flex-direction:column;flex:1}
.thrust h3{font-size:20px;margin-bottom:8px}
.thrust p{color:var(--ink-2);font-size:15px;margin:0 0 12px}
.thrust .who{font-size:13.5px;color:var(--ink-3);border-top:1px solid var(--line-2);padding-top:10px;margin-top:auto}
@media (max-width:980px){.thrusts{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.thrusts{grid-template-columns:1fr}}

/* SUMMIT feature */
.feature{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);background:var(--navy);color:#fff;border-radius:var(--radius);overflow:hidden;margin-bottom:clamp(36px,5vw,56px);isolation:isolate;border:1px solid var(--line)}
.feature .copy{padding:clamp(28px,4vw,52px)}
.feature .kicker{display:inline-block;background:var(--amber);color:#2B1B00;font-weight:500;font-size:13px;padding:4px 10px;border-radius:5px;margin-bottom:18px}
.feature h3{font-size:clamp(24px,2.4vw,32px);color:#fff;margin-bottom:12px}
.feature p{color:var(--on-navy-2);max-width:36em}
.feature .meta{display:grid;grid-template-columns:1fr 1fr;gap:14px 24px;margin-top:22px;padding-top:18px;border-top:1px solid rgba(255,255,255,.15)}
.feature .meta b{display:block;color:#fff;font-weight:600;font-size:15px}
.feature .meta span{font-size:13.5px;color:var(--on-navy-3)}
.feature .visual{position:relative;min-height:320px;background-size:cover;background-position:center}
.feature .visual::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,var(--navy) 0%,rgba(14,32,54,.55) 35%,rgba(14,32,54,.25) 100%)}
.feature .visual svg{position:absolute;inset:0;width:100%;height:100%}
@media (max-width:860px){.feature{grid-template-columns:1fr}.feature .visual{min-height:280px}.feature .visual::before{background:linear-gradient(180deg,var(--navy) 0%,rgba(14,32,54,.45) 40%,rgba(14,32,54,.25) 100%)}}
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
@media (max-width:760px){.director{grid-template-columns:1fr;padding:22px}}
.core{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:18px}
.core .person{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px}
.core .avatar{margin-bottom:16px}
@media (max-width:860px){.core{grid-template-columns:1fr}}
.group{margin-top:48px}
.group h3{font-size:22px;margin-bottom:6px}
.group>p{color:var(--ink-3);font-size:14.5px;margin-bottom:14px}
.plist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.prow{display:flex;gap:16px;padding:16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);align-items:flex-start}
.pname{font-weight:600;display:block}
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

/* publications */
.filters{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;margin-bottom:22px;padding:14px 18px;border:1px solid var(--line);border-radius:var(--radius);background:var(--bg-2)}
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
FEDERATION = """<svg viewBox="0 0 440 440" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SUMMIT federates testbed sites at UMass Lowell, NYU, and West Virginia University">
<defs><radialGradient id="g1" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#0E8FA3" stop-opacity=".6"/><stop offset="1" stop-color="#0E8FA3" stop-opacity="0"/></radialGradient></defs>
<g fill="none" stroke="#FFFFFF" stroke-opacity=".55" stroke-width="1.5">
  <path d="M230 96C180 150 130 195 96 236"/><path d="M230 96C226 180 214 260 200 336"/><path d="M96 236C130 280 165 315 200 336"/>
</g>
<g fill="none" stroke="#E39A16" stroke-width="2.6" stroke-linecap="round">
  <path class="fed-flow" d="M230 96C180 150 130 195 96 236"/><path class="fed-flow" d="M230 96C226 180 214 260 200 336" style="animation-delay:1.1s"/><path class="fed-flow" d="M96 236C130 280 165 315 200 336" style="animation-delay:2.2s"/>
</g>
<g>
  <circle cx="230" cy="96" r="54" fill="url(#g1)"/><circle cx="230" cy="96" r="13" fill="#FFFFFF"/><circle cx="230" cy="96" r="5.5" fill="#0E2036"/>
  <circle cx="96" cy="236" r="40" fill="url(#g1)"/><circle cx="96" cy="236" r="10" fill="#FFFFFF"/>
  <circle cx="200" cy="336" r="40" fill="url(#g1)"/><circle cx="200" cy="336" r="10" fill="#FFFFFF"/>
</g>
<g font-family="IBM Plex Sans, Arial, sans-serif" fill="#FFFFFF" font-size="15">
  <text x="254" y="90" font-weight="600">UMass Lowell</text><text x="254" y="109" fill="#C9D3E0" font-size="13">lead site, instrument host</text>
  <text x="40" y="274" font-weight="600">NYU Tandon</text><text x="40" y="293" fill="#C9D3E0" font-size="13">Yuzhang Lin, Co-PI</text>
  <text x="222" y="342" font-weight="600" font-size="14">West Virginia University</text><text x="222" y="361" fill="#C9D3E0" font-size="13">partner site</text>
</g>
</svg>"""

# cyber-physical loop schematic (About section)
SCHEMATIC = """<svg viewBox="0 0 660 424" role="img" aria-labelledby="schemTitle schemDesc" xmlns="http://www.w3.org/2000/svg">
<title id="schemTitle">How a smart cyber-physical system closes the loop</title>
<desc id="schemDesc">Physical systems in energy, transportation, and healthcare are sensed, connected over a secure network, analysed by AI at the edge and cloud, and controlled in real time.</desc>
<defs>
  <marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0.5 8 4 0 7.5z" fill="#0E2036"/></marker>
</defs>
<g font-family="IBM Plex Sans, Arial, sans-serif" font-size="15" fill="#0E2036">
  <text x="70" y="26" text-anchor="middle" fill="#5B6B82">physical world</text>
  <text x="320" y="26" text-anchor="middle" fill="#5B6B82">secure network</text>
  <text x="538" y="26" text-anchor="middle" fill="#5B6B82">compute and control</text>

  <g stroke="#0E2036" stroke-width="1.7" fill="#fff" stroke-linecap="round" stroke-linejoin="round">
    <g transform="translate(40,54)">
      <path d="M8 46V14l22-10 22 10v32M8 46h44"/><path d="M18 24h24M18 34h24"/><path d="M0 46h60"/>
      <path d="M4 56c11 0 11 8 22 8s11-8 22-8" stroke="#0E8FA3" stroke-width="1.6"/>
    </g>
    <g transform="translate(40,170)">
      <path d="M6 30h48l-6-14H14z"/><circle cx="16" cy="34" r="5"/><circle cx="44" cy="34" r="5"/>
      <path d="M0 42h60" stroke-dasharray="6 5"/><path d="M30 8V2M23 6l-4-4M37 6l4-4" stroke="#0E8FA3" stroke-width="1.6"/>
    </g>
    <g transform="translate(40,284)">
      <rect x="6" y="4" width="48" height="40" rx="4"/><path d="M30 14v20M20 24h20"/>
      <path d="M2 56c8 0 9-12 16-12s7 20 14 20 6-14 13-14 7 6 13 6" stroke="#0E8FA3" stroke-width="1.6"/>
    </g>
  </g>
  <text x="70" y="140" text-anchor="middle">energy and power</text>
  <text x="70" y="236" text-anchor="middle">transportation</text>
  <text x="70" y="370" text-anchor="middle">healthcare</text>

  <g fill="#fff" stroke="#0E2036" stroke-width="1.7">
    <rect x="176" y="80" width="38" height="38" rx="7"/><rect x="176" y="194" width="38" height="38" rx="7"/><rect x="176" y="302" width="38" height="38" rx="7"/>
  </g>
  <g font-size="13" text-anchor="middle"><text x="195" y="104">edge</text><text x="195" y="218">edge</text><text x="195" y="326">edge</text></g>

  <g stroke="#0E2036" stroke-width="1.2" fill="none"><path d="M106 99H172"/><path d="M106 213H172"/><path d="M106 321H172"/></g>
  <g stroke="#E39A16" stroke-width="2.6" fill="none" stroke-linecap="round">
    <path class="flow" d="M106 99H172"/><path class="flow slow" d="M106 213H172"/><path class="flow" d="M106 321H172"/>
  </g>

  <g transform="translate(322,213)">
    <circle r="64" fill="#fff" stroke="#0E2036" stroke-width="1.7"/>
    <circle r="64" fill="none" stroke="#0E8FA3" stroke-width="2.4" class="flow slow"/>
    <circle r="6" fill="#0E2036"/>
    <g fill="#0E2036"><circle cx="0" cy="-64" r="4.5"/><circle cx="55" cy="-32" r="4.5"/><circle cx="55" cy="32" r="4.5"/><circle cx="0" cy="64" r="4.5"/><circle cx="-55" cy="32" r="4.5"/><circle cx="-55" cy="-32" r="4.5"/></g>
    <g stroke="#0E2036" stroke-width="1" opacity=".5"><path d="M0-64 0 64M55-32-55 32M55 32-55-32"/></g>
    <text y="-78" text-anchor="middle" font-size="13.5">optical and 5G/6G transport</text>
    <text y="92" text-anchor="middle" font-size="13.5">zero trust, attestation, IDS</text>
  </g>

  <g stroke="#0E2036" stroke-width="1.2" fill="none">
    <path d="M214 99C244 99 248 150 266 176"/><path d="M214 213H256"/><path d="M214 321C244 321 248 274 266 250"/>
  </g>
  <g stroke="#0E8FA3" stroke-width="2.6" fill="none" stroke-linecap="round">
    <path class="flow" d="M214 99C244 99 248 150 266 176"/><path class="flow slow" d="M214 213H256"/><path class="flow" d="M214 321C244 321 248 274 266 250"/>
  </g>

  <g transform="translate(446,136)">
    <rect width="186" height="154" rx="9" fill="#fff" stroke="#0E2036" stroke-width="1.7"/>
    <text x="93" y="32" text-anchor="middle" font-weight="600" font-size="15">AI, digital twins, HPC</text>
    <g stroke="#0E2036" stroke-width="1.3" fill="none">
      <rect x="16" y="48" width="154" height="22" rx="4"/><rect x="16" y="76" width="154" height="22" rx="4"/><rect x="16" y="104" width="154" height="22" rx="4"/>
    </g>
    <g font-size="12" fill="#2B4162"><text x="24" y="63">anomaly detection</text><text x="24" y="91">state estimation</text><text x="24" y="119">planning, optimization</text></g>
    <g fill="#E39A16"><circle cx="160" cy="59" r="3.5" class="pulse"/><circle cx="160" cy="87" r="3.5" class="pulse" style="animation-delay:1s"/><circle cx="160" cy="115" r="3.5" class="pulse" style="animation-delay:2s"/></g>
    <text x="93" y="144" text-anchor="middle" font-size="12" fill="#5B6B82">edge to cloud</text>
  </g>

  <g stroke="#0E2036" stroke-width="1.2" fill="none"><path d="M386 199H442" marker-end="url(#arr)"/><path d="M442 227H388" marker-end="url(#arr)"/></g>
  <g stroke="#0E8FA3" stroke-width="2.6" fill="none" stroke-linecap="round"><path class="flow" d="M386 199H432"/></g>
  <g stroke="#E39A16" stroke-width="2.6" fill="none" stroke-linecap="round"><path class="flow" d="M432 227H396"/></g>
  <text x="414" y="189" text-anchor="middle" font-size="12" fill="#5B6B82">telemetry</text>
  <text x="414" y="246" text-anchor="middle" font-size="12" fill="#5B6B82">control</text>

  <path d="M539 291V396H70V384" fill="none" stroke="#0E2036" stroke-width="1.2" stroke-dasharray="4 4" marker-end="url(#arr)"/>
  <text x="330" y="416" text-anchor="middle" font-size="13" fill="#5B6B82">closed loop: sense, communicate, decide, act</text>
</g>
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
     "Vokkarane, Arias, Tseng, with Yuzhang Lin (NYU)"),
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
     "Xie, Tseng, Cao, Yu, Inalpolat, Aghara, Robinette, Mathew"),
]

# ---------------------------------------------------------------- themed SVG helpers
_COLOR_CLASS = {
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
_ART_HEAD = '<svg viewBox="0 0 360 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" fill="none" stroke="#0E2036" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'

ART = {
"grid": _ART_HEAD + """
<!-- transmission towers -->
<g>
  <path d="M46 150L60 42h12l14 108M50 122h36M53 96h30M57 70h22"/><path d="M40 122h56M44 96h48M50 70h36"/>
  <path d="M292 150l14-108h12l14 108M296 122h36M299 96h30M303 70h22"/><path d="M286 122h56M290 96h48M296 70h36"/>
</g>
<!-- lines sagging between towers -->
<path d="M44 96Q180 150 290 96M50 70Q180 118 296 70" stroke-width="1.2"/>
<!-- substation -->
<rect x="140" y="112" width="80" height="38" rx="4" fill="#fff"/>
<path d="M156 150v-38M172 150v-38M188 150v-38M204 150v-38" stroke-width="1.1" stroke="#5B6B82"/>
<path d="M140 128h80" stroke-width="1.1" stroke="#5B6B82"/>
<!-- smart meters -->
<g fill="#fff">
  <rect x="100" y="24" width="30" height="34" rx="5"/><rect x="165" y="24" width="30" height="34" rx="5"/><rect x="230" y="24" width="30" height="34" rx="5"/>
</g>
<g stroke="#0E8FA3"><path d="M106 44a9 9 0 0 1 18 0M171 44a9 9 0 0 1 18 0M236 44a9 9 0 0 1 18 0"/><path d="M115 44l5-6M180 44l4-7M245 44l3-8"/></g>
<!-- telemetry to control -->
<g stroke="#0E8FA3" stroke-dasharray="3 6" stroke-width="1.8"><path d="M115 58v54M180 58v54M245 58v54"/></g>
<!-- shield over the substation -->
<path d="M180 76l14 5v10c0 9-6 15-14 18-8-3-14-9-14-18V81z" fill="#E3F3F6" stroke="#0E8FA3" stroke-width="1.8"/>
<path d="M174 91l4 4 8-9" stroke="#0E8FA3" stroke-width="1.8"/>
<!-- attack bolt deflected -->
<path d="M262 70l-16 10 8 2-10 14" stroke="#E39A16" stroke-width="2"/>
<circle cx="242" cy="98" r="3" fill="#E39A16" stroke="none"/>
<path d="M20 150h320" stroke="#5B6B82" stroke-width="1.1"/>
</svg>""",

"ai": _ART_HEAD + """
<!-- neural network -->
<g fill="#fff">
  <circle cx="46" cy="60" r="8"/><circle cx="46" cy="92" r="8"/><circle cx="46" cy="124" r="8"/>
  <circle cx="96" cy="44" r="8"/><circle cx="96" cy="76" r="8"/><circle cx="96" cy="108" r="8"/><circle cx="96" cy="140" r="8"/>
  <circle cx="146" cy="76" r="8"/><circle cx="146" cy="108" r="8"/>
</g>
<g stroke="#5B6B82" stroke-width="1">
  <path d="M54 60L88 44M54 60L88 76M54 60L88 108M54 92L88 44M54 92L88 76M54 92L88 108M54 92L88 140M54 124L88 76M54 124L88 108M54 124L88 140"/>
  <path d="M104 44L138 76M104 76L138 76M104 108L138 108M104 140L138 108M104 76L138 108M104 108L138 76"/>
</g>
<circle cx="146" cy="76" r="3" fill="#0E8FA3" stroke="none"/><circle cx="146" cy="108" r="3" fill="#0E8FA3" stroke="none"/>
<!-- safety gate -->
<rect x="176" y="70" width="44" height="44" rx="8" fill="#E3F3F6" stroke="#0E8FA3" stroke-width="1.8"/>
<path d="M188 92h20M198 82v20" stroke="#0E8FA3" stroke-width="1.8"/>
<path d="M154 92h22M220 92h22" stroke="#0E8FA3" stroke-width="1.8" marker-end="none"/>
<path d="M238 88l6 4-6 4" stroke="#0E8FA3" stroke-width="1.8"/>
<!-- plant: turbine and gauge -->
<circle cx="292" cy="92" r="34" fill="#fff"/>
<path d="M292 92l-18-14M292 92l20-10M292 92l-2 24" stroke-width="1.4"/>
<circle cx="292" cy="92" r="5" fill="#fff"/>
<path d="M268 128a34 34 0 0 0 48 0" stroke="#5B6B82" stroke-width="1.2"/>
<!-- feedback loop back to the network -->
<path d="M292 132V152H46V136" stroke="#E39A16" stroke-width="1.6" stroke-dasharray="4 5"/>
<path d="M42 142l4-6 4 6" stroke="#E39A16" stroke-width="1.6"/>
<text x="180" y="150" font-family="IBM Plex Sans, Arial, sans-serif" font-size="11" fill="#5B6B82" stroke="none" text-anchor="middle">learn, check, act</text>
</svg>""",

"fiber": _ART_HEAD + """
<!-- fiber cross-section -->
<circle cx="62" cy="92" r="38" fill="#fff"/><circle cx="62" cy="92" r="26" stroke="#5B6B82" stroke-width="1.2"/><circle cx="62" cy="92" r="9" fill="#E3F3F6" stroke="#0E8FA3"/>
<g fill="#0E8FA3" stroke="none"><circle cx="62" cy="92" r="2.5"/><circle cx="52" cy="80" r="2"/><circle cx="74" cy="82" r="2"/><circle cx="50" cy="104" r="2"/><circle cx="74" cy="104" r="2"/></g>
<!-- spectrum axis with bands -->
<path d="M126 128h150" stroke="#5B6B82" stroke-width="1.2"/>
<g stroke="none">
  <rect x="130" y="72" width="40" height="56" fill="#E3F3F6"/><rect x="176" y="56" width="44" height="72" fill="#0E8FA3" opacity=".75"/><rect x="226" y="84" width="46" height="44" fill="#E39A16" opacity=".8"/>
</g>
<g stroke="#0E2036" stroke-width="1.2"><path d="M130 72h40v56M176 56h44v72M226 84h46v44"/></g>
<g font-family="IBM Plex Sans, Arial, sans-serif" font-size="11" fill="#5B6B82" stroke="none" text-anchor="middle"><text x="150" y="144">S</text><text x="198" y="144">C</text><text x="249" y="144">L</text><text x="201" y="162">multi-band spectrum</text></g>
<!-- 6G mast -->
<path d="M320 150V70M312 150h16" stroke-width="1.4"/><path d="M314 70h12l-6-10z" fill="#fff"/>
<g stroke="#0E8FA3" stroke-width="1.6"><path d="M306 64a20 20 0 0 1 28 0M300 56a29 29 0 0 1 40 0"/></g>
<!-- link from fiber to spectrum -->
<path d="M100 92h24" stroke="#0E8FA3" stroke-width="1.8" stroke-dasharray="3 6"/>
</svg>""",

"edge": _ART_HEAD + """
<!-- replicated cluster -->
<g fill="#fff"><rect x="60" y="60" width="34" height="26" rx="5"/><rect x="128" y="36" width="34" height="26" rx="5"/><rect x="196" y="60" width="34" height="26" rx="5"/><rect x="94" y="118" width="34" height="26" rx="5"/><rect x="162" y="118" width="34" height="26" rx="5"/></g>
<g stroke="#5B6B82" stroke-width="1.1"><path d="M94 73h34M162 62l34 11M77 86l17 32M213 86l-17 32M128 131h34M94 73l34-11M145 62v56"/></g>
<g stroke="#0E8FA3" stroke-width="1.8"><path d="M70 74l4 4 8-8M138 50l4 4 8-8M206 74l4 4 8-8M104 132l4 4 8-8"/></g>
<!-- one faulty node -->
<path d="M172 126l14 12M186 126l-14 12" stroke="#E39A16" stroke-width="2"/>
<!-- drone -->
<g transform="translate(272,54)"><path d="M0 12h40M8 12v-6h-8M32 12v-6h8" stroke-width="1.4"/><rect x="12" y="10" width="16" height="9" rx="2" fill="#fff"/><path d="M-6 6h12M34 6h12" stroke="#5B6B82"/></g>
<!-- satellite arc and link -->
<path d="M262 36a48 48 0 0 1 60 0" stroke="#0E8FA3" stroke-width="1.4" stroke-dasharray="3 5"/>
<circle cx="292" cy="20" r="4" fill="#0E8FA3" stroke="none"/>
<path d="M292 74v40" stroke="#0E8FA3" stroke-width="1.8" stroke-dasharray="3 6"/>
<path d="M292 114l-62 14" stroke="#0E8FA3" stroke-width="1.4" stroke-dasharray="3 6"/>
<text x="292" y="146" font-family="IBM Plex Sans, Arial, sans-serif" font-size="11" fill="#5B6B82" stroke="none" text-anchor="middle">edge</text>
<text x="145" y="164" font-family="IBM Plex Sans, Arial, sans-serif" font-size="11" fill="#5B6B82" stroke="none" text-anchor="middle">consensus with a faulty replica</text>
</svg>""",

"chip": _ART_HEAD + """
<!-- chip package -->
<rect x="70" y="52" width="88" height="88" rx="8" fill="#fff"/>
<rect x="92" y="74" width="44" height="44" rx="4" fill="#E3F3F6" stroke="#0E8FA3"/>
<g stroke-width="1.3"><path d="M86 52V38M102 52V38M118 52V38M134 52V38M86 140v14M102 140v14M118 140v14M134 140v14M70 70H56M70 88H56M70 106H56M70 124H56M158 70h14M158 88h14M158 106h14M158 124h14"/></g>
<!-- lock on die -->
<rect x="106" y="94" width="16" height="13" rx="2" fill="#fff" stroke="#0E8FA3" stroke-width="1.6"/><path d="M109 94v-4a5 5 0 0 1 10 0v4" stroke="#0E8FA3" stroke-width="1.6"/>
<!-- hardware counters -->
<g stroke="none" fill="#0E8FA3"><rect x="204" y="98" width="10" height="42"/><rect x="220" y="80" width="10" height="60"/><rect x="236" y="110" width="10" height="30"/><rect x="252" y="66" width="10" height="74"/></g>
<rect x="268" y="120" width="10" height="20" fill="#E39A16" stroke="none"/>
<path d="M198 140h90" stroke="#5B6B82" stroke-width="1.2"/>
<text x="243" y="156" font-family="IBM Plex Sans, Arial, sans-serif" font-size="11" fill="#5B6B82" stroke="none" text-anchor="middle">hardware counters</text>
<!-- rack -->
<rect x="300" y="44" width="40" height="96" rx="4" fill="#fff"/>
<g stroke="#5B6B82" stroke-width="1.1"><path d="M300 64h40M300 84h40M300 104h40M300 124h40"/></g>
<g fill="#0E8FA3" stroke="none"><circle cx="332" cy="54" r="2"/><circle cx="332" cy="74" r="2"/><circle cx="332" cy="94" r="2"/><circle cx="332" cy="114" r="2"/></g>
<path d="M172 96h26" stroke="#0E8FA3" stroke-width="1.8" stroke-dasharray="3 6"/>
</svg>""",

"health": _ART_HEAD + """
<!-- road with connected vehicles -->
<path d="M20 132h200" stroke-width="1.4"/><path d="M28 126h184" stroke="#5B6B82" stroke-width="1" stroke-dasharray="10 8"/>
<g fill="#fff"><path d="M44 120h52l-8-16H56z"/><path d="M130 120h52l-8-16h-36z"/></g>
<g fill="#fff"><circle cx="54" cy="122" r="5"/><circle cx="86" cy="122" r="5"/><circle cx="140" cy="122" r="5"/><circle cx="172" cy="122" r="5"/></g>
<path d="M92 96q32-26 64 0" stroke="#0E8FA3" stroke-width="1.6" stroke-dasharray="3 5"/>
<g stroke="#0E8FA3" stroke-width="1.4"><path d="M70 98v-8M64 92l6-6 6 6M156 98v-8M150 92l6-6 6 6"/></g>
<!-- bridge with sensors -->
<path d="M240 132h100M250 132V96M330 132V96M240 96h100" stroke-width="1.4"/>
<path d="M250 96q40-36 80 0" stroke-width="1.4"/><path d="M270 132V84M290 132V76M310 132V84" stroke="#5B6B82" stroke-width="1"/>
<g fill="#E39A16" stroke="none"><circle cx="270" cy="84" r="3"/><circle cx="290" cy="76" r="3"/><circle cx="310" cy="84" r="3"/></g>
<!-- hospital and ECG -->
<rect x="236" y="26" width="44" height="40" rx="5" fill="#fff"/><path d="M258 36v20M248 46h20" stroke="#0E8FA3" stroke-width="2"/>
<path d="M288 50h10l6-14 8 28 8-20 6 8h12" stroke="#0E8FA3" stroke-width="1.8"/>
<!-- data uplinks -->
<path d="M120 60h96" stroke="#0E8FA3" stroke-width="1.4" stroke-dasharray="3 6"/>
<circle cx="120" cy="60" r="4" fill="#0E8FA3" stroke="none"/>
<path d="M120 64v32" stroke="#0E8FA3" stroke-width="1.4" stroke-dasharray="3 6"/>
<text x="180" y="160" font-family="IBM Plex Sans, Arial, sans-serif" font-size="11" fill="#5B6B82" stroke="none" text-anchor="middle">connected roads, hospitals, and structures</text>
</svg>""",
}
ART = {k: theme_svg(v) for k, v in ART.items()}
SCHEMATIC = theme_svg(SCHEMATIC)

def person_card(p, size="lg", with_photo=True):
    lines = []
    if with_photo:
        lines.append(avatar(p, size))
    lines += [f'<h3>{esc(p["name"])}</h3>', f'<p class="ptitle">{esc(p["title"])}</p>', f'<p class="pareas">{esc(p["areas"])}</p>']
    if p.get("role"):
        lines.append(f'<p class="prole">{esc(p["role"])}</p>')
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(f'<span>{esc(p["phone"])}</span>')
    if p.get("office"): meta.append(f'<span>{esc(p["office"])}</span>')
    if p.get("url"): meta.append(f'<a href="{esc(p["url"])}">UMass Lowell profile</a>')
    lines.append('<p class="pmeta">' + " ".join(f'<span class="mi">{m}</span>' for m in meta) + '</p>')
    return '<article class="person">' + "".join(lines) + '</article>'

def person_row(p):
    meta = []
    if p.get("email"): meta.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
    if p.get("phone"): meta.append(esc(p["phone"]))
    return ('<li class="prow">' + avatar(p, "sm") + '<div><span class="pname">' + esc(p["name"]) + '</span><span class="ptitle2">' + esc(p["title"]) + '</span>'
            '<span class="pareas2">' + esc(p["areas"]) + '</span><div class="pcontact">' + '<span class="sep"></span>'.join(meta) + '</div></div></li>')

# ---------------------------------------------------------------- counts
n_pubs = len(P)
n_journal = sum(1 for p in P if p["type"] == "journal")
n_faculty = 1 + len(FACULTY["core"]) + len(FACULTY["board"]) + len(FACULTY["affiliated"])

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
    board_html = '<ul class="plist">' + "".join(person_row(p) for p in FACULTY["board"]) + '</ul>'
    aff_html = '<ul class="plist">' + "".join(person_row(p) for p in FACULTY["affiliated"]) + '</ul>'
    partners_html = '<ul class="partners">' + "".join(
        f'<li><b>{esc(c["name"])}</b><span>{esc(c["org"])}</span><span>{esc(c["note"])}</span></li>' for c in FACULTY["collaborators"]) + '</ul>'

    news_html = "".join(f'<li><time>{esc(w)}</time><p>{esc(t)}</p></li>' for w, t in NEWS)

    def render_pubs(items):
        out = ""
        cur = None
        for p in items:
            if p["year"] != cur:
                if cur is not None: out += "</ul>"
                cur = p["year"]; out += f'<div class="yearhead">{cur}</div><ul class="pubs">'
            kind = '<span class="kind j">Journal</span>' if p["type"] == "journal" else '<span class="kind">Conference</span>'
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
        (str(n_pubs), f"peer-reviewed papers since 2025, {n_journal} of them in journals"),
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
    <a class="brand" href="#top" aria-label="SCyPS home">{LOGO}<span>SCyPS<small>Center for Smart Cyber-Physical Systems, UMass Lowell</small></span></a>
    <div class="navright">
    <ul class="links" id="menu">
      <li><a href="#about">About</a></li>
      <li><a href="#research">Research</a></li>
      <li><a href="#projects">Projects</a></li>
      <li><a href="#people">People</a></li>
      <li><a href="#publications">Publications</a></li>
      <li><a href="#news">News</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <button class="theme" id="theme" type="button" aria-label="Switch to dark mode"><svg class="moon" viewBox="0 0 24 24"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/></svg><span class="lbl">Dark</span></button>
    <button class="navtoggle" aria-expanded="false" aria-controls="menu">Menu</button>
    </div>
  </div>
</header>

<main id="main">
<div class="hero" id="top">
  <div class="bg" role="img" aria-label="City skyline overlaid with a wireless communication network"{hero_bg}></div>
  <div class="veil"></div>
  <div class="wrap">
    <h1>Where computation meets the physical world.</h1>
    <p class="lede">Power grids, roads, and hospitals now run on networks, sensors, and software. The Center for Smart Cyber-Physical Systems brings UMass Lowell researchers in networking, security, distributed computing, hardware, and AI together with domain experts to keep that infrastructure secure, resilient, and working under attack, failure, and disaster.</p>
    <div class="cta"><a class="btn primary" href="#research">Explore our research</a><a class="btn" href="#publications">Recent publications</a></div>
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
    <div class="shead"><h2>Funded projects</h2><p>Active sponsored research led by center faculty. Three new awards started in 2026, headed by the NSF MRI SUMMIT testbed.</p></div>
    <div class="feature">
      <div class="copy">
        <span class="kicker">New in 2026</span>
        <h3>SUMMIT: a three-site smart grid testbed you can attack, defend, and restore</h3>
        <p>NSF's Major Research Instrumentation program is funding a federated cyber-physical instrument that links real-time power system simulation, grid communication networks, and protection and control devices across UMass Lowell, NYU, and West Virginia University. Researchers at any site will be able to run attack, defense, and restoration experiments on the shared testbed, and students will train on the same equipment utilities and vendors use.</p>
        <div class="meta">
          <div><b>$2.0M</b><span>NSF MRI Track 2, Award #2511635</span></div>
          <div><b>Oct 2026 to Sep 2029</b><span>award period</span></div>
          <div><b>Vinod Vokkarane, PI</b><span>Co-PIs Orlando Arias, Lewis Tseng, Yuzhang Lin</span></div>
          <div><b>Postdoc search open</b><span>postdoctoral research associate, Fall 2026</span></div>
        </div>
      </div>
      <div class="visual"{cyber_bg}>{FEDERATION}</div>
    </div>
    <div class="ledger">{projects_html}</div>
    <div class="tools">{tools_html}</div>
  </div>
</section>

<section id="people" class="tint">
  <div class="wrap">
    <div class="shead"><h2>People</h2><p>Faculty from the Francis College of Engineering, the Kennedy College of Sciences, and UMass Chan Medical School, plus long-running collaborators at partner universities and companies.</p></div>
    {director_html}
    {core_html}
    <div class="group"><h3>Board of directors</h3><p>Center governance and cross-college leadership.</p>{board_html}</div>
    <div class="group"><h3>Affiliated researchers</h3><p>Faculty who collaborate on center projects and proposals.</p>{aff_html}</div>
    <div class="group"><h3>Partners and collaborators</h3><p>Institutions and companies the center works with on current projects.</p>{partners_html}</div>
  </div>
</section>

<section id="publications">
  <div class="wrap">
    <div class="shead"><h2>Publications</h2><p>Peer-reviewed journal and conference papers from center faculty since January 2025, with links to the publisher's record. Center faculty are shown in bold.</p></div>
    <div class="filters" role="group" aria-label="Filter publications">
      <div class="fgroup"><span class="lab">Faculty</span>
        <button class="chip" data-f="fac" data-v="all" aria-pressed="true">All</button>
        <button class="chip" data-f="fac" data-v="Vokkarane" aria-pressed="false">Vokkarane</button>
        <button class="chip" data-f="fac" data-v="Arias" aria-pressed="false">Arias</button>
        <button class="chip" data-f="fac" data-v="Tseng" aria-pressed="false">Tseng</button>
        <button class="chip" data-f="fac" data-v="Son" aria-pressed="false">Son</button>
      </div>
      <div class="fgroup"><span class="lab">Type</span>
        <button class="chip" data-f="type" data-v="all" aria-pressed="true">All</button>
        <button class="chip" data-f="type" data-v="journal" aria-pressed="false">Journal</button>
        <button class="chip" data-f="type" data-v="conference" aria-pressed="false">Conference</button>
      </div>
      <div class="search"><label for="q" class="lab">Search</label><input id="q" type="search" placeholder="title, author, or venue" autocomplete="off"></div>
    </div>
    <div class="count" id="count" aria-live="polite">Showing {n_pubs} of {n_pubs} papers</div>
    <div id="publist">{pubs_html}</div>
    <p class="pubnote">Records verified against Crossref; the NSDI paper is listed from the USENIX program. Send corrections or additions to SCyPS@uml.edu.</p>
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
      </div>
    </div>
  </div>
</section>
</main>

<footer id="contact" class="uml-footer" role="contentinfo">
  <div class="wrap">
    <div class="cols">
      <div class="col">
        <a href="https://www.uml.edu/" title="UMass Lowell home">{UML_LOGO}</a>
        <address><strong>Center for Smart Cyber-Physical Systems (SCyPS)</strong><br>UMass Lowell<br>1 University Ave. Lowell, MA 01854<br>Email: <a href="mailto:SCyPS@uml.edu">SCyPS@uml.edu</a></address>
      </div>
      <div class="col menu">
        <nav aria-label="Footer menu"><h2>Menu</h2>
          <ul><li><a href="#about">About</a></li><li><a href="#research">Research</a></li><li><a href="#projects">Projects</a></li><li><a href="#people">People</a></li><li><a href="#publications">Publications</a></li><li><a href="#news">News</a></li></ul>
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

  var state={{fac:'all',type:'all',q:''}};
  var items=[].slice.call(document.querySelectorAll('#publist .pubs li'));
  var total=items.length, count=document.getElementById('count');
  function apply(){{
    var q=state.q.trim().toLowerCase(), shown=0;
    items.forEach(function(li){{
      var ok=(state.fac==='all'||li.getAttribute('data-fac').split(' ').indexOf(state.fac)>-1)
          &&(state.type==='all'||li.getAttribute('data-type')===state.type)
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
