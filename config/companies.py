"""Companies whose job board is served by a known applicant tracking system.

Adding one of these needs no code: append an entry here and it becomes a parser at
startup via parsers/ats.py::load_ats_parsers(). Companies whose careers site is not on
a supported ATS need a real parser in parsers/ instead -- see
docs/companies_without_ats.md for the ones that were skipped.

    name   company shown in the Telegram notification
    ats    greenhouse | lever | ashby | smartrecruiters | workable | recruitee
           | personio | comeet | workday
    token  the board identifier used by that ATS

Workday entries also need "wd" (datacenter) and "site"; Comeet needs "company".
"""

COMPANIES = [

    {"name": "Aqua Security", "ats": "comeet",
     "token": "191644966966644E194B3191644644", "company": "91.001"},
    {"name": "Avertium", "ats": "lever", "token": "avertium"},
    {"name": "Broadcom", "ats": "workday",
     "token": "broadcom", "site": "External_Career", "wd": "wd1"},
    {"name": "Cado Security (Darktrace)", "ats": "workday",
     "token": "darktrace", "site": "DarktaceExternal", "wd": "wd3"},
    {"name": "Chainalysis", "ats": "ashby", "token": "chainalysis-careers"},
    {"name": "CloudSEK", "ats": "greenhouse", "token": "cloudsek"},
    {"name": "Cybereason", "ats": "greenhouse", "token": "cybereason"},
    {"name": "Dragos", "ats": "greenhouse", "token": "dragos"},
    {"name": "Elliptic", "ats": "ashby", "token": "elliptic"},
    {"name": "F5", "ats": "workday", "token": "ffive", "site": "f5jobs", "wd": "wd5"},
    {"name": "Flashpoint", "ats": "ashby", "token": "flashpoint.io"},
    {"name": "Group-IB", "ats": "greenhouse", "token": "groupib"},
    {"name": "GuidePoint Security", "ats": "greenhouse", "token": "guidepointsecurity"},
    {"name": "Huntress", "ats": "greenhouse", "token": "huntress"},
    {"name": "Iru (formerly Kandji)", "ats": "lever", "token": "iru"},
    {"name": "Jamf", "ats": "greenhouse", "token": "jamf"},
    {"name": "Juniper (HPE)", "ats": "workday",
     "token": "hpe", "site": "Jobsathpe", "wd": "wd5"},
    {"name": "KnowBe4", "ats": "greenhouse", "token": "knowbe4"},
    {"name": "Magnet Forensics", "ats": "lever", "token": "magnetforensics"},
    {"name": "McAfee", "ats": "greenhouse", "token": "mcafee"},
    {"name": "Menlo Security", "ats": "ashby", "token": "menlosecurity"},
    {"name": "Mozilla", "ats": "greenhouse", "token": "mozilla"},
    {"name": "Netskope", "ats": "greenhouse", "token": "netskope"},
    {"name": "Panda Security (WatchGuard)", "ats": "lever", "token": "watchguard"},
    {"name": "Phylum (Veracode)", "ats": "greenhouse", "token": "veracode"},
    {"name": "Picus Security", "ats": "lever", "token": "picus"},
    {"name": "PortSwigger", "ats": "workable", "token": "portswigger"},
    {"name": "Praetorian", "ats": "greenhouse", "token": "praetorian"},
    {"name": "Proofpoint", "ats": "workday",
     "token": "proofpoint", "site": "proofpointcareers", "wd": "wd5"},
    {"name": "Recorded Future", "ats": "greenhouse", "token": "recordedfuture"},
    {"name": "ReversingLabs", "ats": "smartrecruiters", "token": "reversinglabs"},
    {"name": "S-RM", "ats": "greenhouse", "token": "srm"},
    {"name": "Socket", "ats": "ashby", "token": "socket"},
    {"name": "Sophos", "ats": "lever", "token": "sophos"},
    {"name": "SpecterOps", "ats": "greenhouse", "token": "specterops"},
    {"name": "Sysdig", "ats": "lever", "token": "sysdig"},
    {"name": "Tenable", "ats": "greenhouse", "token": "tenableinc"},
    {"name": "Trail of Bits", "ats": "workable", "token": "trailofbits"},
    {"name": "Tripwire (Fortra)", "ats": "workday",
     "token": "fortra", "site": "FortraCareers", "wd": "wd12"},
    {"name": "TRM Labs", "ats": "ashby", "token": "trm-labs"},
    {"name": "UpGuard", "ats": "lever", "token": "upguard"},
    {"name": "Zimperium", "ats": "lever", "token": "zimperium"},
    {"name": "Zscaler", "ats": "greenhouse", "token": "zscaler"},
]
