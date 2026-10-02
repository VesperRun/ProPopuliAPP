from sqlalchemy.orm import Session

from app.models import Hub

DEFAULT_HUBS: list[tuple[str, str, str]] = [
    ("general", "General", "Start here. Recast critiques before you publish."),
    ("build", "Build", "Ship work, ask sharp questions, improve ideas."),
    ("welcome", "Welcome", "Introduce yourself and what you're here to discuss—handles only, no doxxing."),
    ("norms", "Norms", "How we argue here: reframe, cite, disagree without teardown."),
    (
        "gate-notes",
        "Gate Notes",
        "Posts challenged by the Reframing Gate—share rewrites that worked.",
    ),
    ("steelman", "Steelman", "Restate the strongest version of an idea before you push back."),
    ("drafts", "Drafts", "Work-in-progress posts and threads—feedback before you go wide."),
    ("questions", "Big Questions", "Open-ended topics where the goal is clarity, not winning."),
    ("ship-log", "Ship Log", "What you shipped this week on any project—small wins count."),
    ("debug", "Debug", "Stuck on a bug or design choice—describe context, ask sharply."),
    (
        "propopuli",
        "ProPopuli",
        "Meta: subpops, UX, moderation—feature ideas and friction reports.",
    ),
    ("civic", "Civic", "Policy and community issues—propose fixes, not pile-ons."),
    ("local-tools", "Local Tools", "Mutual aid, orgs, and practical civic how-to (not corridor-specific)."),
    ("reading", "Reading", "Books, essays, and threads worth a careful reply."),
    ("off-topic", "Off Topic", "Low-stakes chat—still no harassment or policy violations."),
    ("austin", "Austin", "All things Austin, TX — news, culture, and local life."),
    ("spurs-fans", "Spurs Fans", "San Antonio Spurs basketball — games, roster, and fan talk."),
    ("san-antonio", "San Antonio", "The Alamo City — events, food, and local discussion."),
    ("austin-tables", "Austin Tables", "Restaurants, food trucks, and dining in Austin."),
    ("univ-tex-austin", "Univ. of Texas at Austin", "Campus life, academics, and UT Austin community."),
    ("austin-answers", "Austin Answers", "Questions about Austin — newcomers and locals welcome."),
    ("austin-sendup", "Austin Send-up", "Satire and in-jokes about Austin (keep it good-natured)."),
    ("univ-tex-sports", "Univ. of Texas Sports", "Longhorn athletics — football, basketball, and more."),
    ("austin-hiring", "Austin Hiring", "Jobs, gigs, and hiring in the Austin area."),
    ("san-marcos", "San Marcos", "San Marcos, TX — river, campus town, and Hill Country nearby."),
    ("round-rock", "Round Rock", "Round Rock and Williamson County."),
    ("austin-swap", "Austin Swap", "Classifieds — buy, sell, and trade in Austin."),
    ("austin-soccer", "Austin Soccer Fans", "Austin FC and local soccer."),
    ("zilker-fest", "Zilker Fest", "Fan talk around Austin’s big Zilker Park music weekends."),
    ("austin-plots", "Austin Plots", "Gardening and native plants in the Austin area."),
    ("utsa", "UTSA", "University of Texas at San Antonio — Birds up!"),
    ("austin-meetups", "Austin Meetups", "Friends, activity partners, and social connections in ATX."),
    ("pflugerville", "Pflugerville", "Pflugerville and northeast Austin suburbs."),
    ("boerne", "Boerne", "Boerne and Kendall County, northwest of San Antonio."),
    ("austin-wheels", "Austin Wheels", "Cycling and two-wheeled life in Austin."),
    ("cedar-park", "Cedar Park", "Cedar Park, TX."),
    ("texas-state", "Texas State", "Texas State University and San Marcos Bobcats."),
    ("georgetown-tx", "Georgetown", "Georgetown, TX — north of Austin."),
    (
        "south-by-southwest",
        "South by Southwest",
        "Fan discussion around SXSW — music, film, and interactive (not official).",
    ),
    ("new-braunfels", "New Braunfels", "New Braunfels — between San Antonio and Austin."),
    ("univ-tex-admit", "Univ. of Texas Admissions", "Applying to UT Austin — essays, deadlines, and advice."),
    ("leander", "Leander", "Leander and northwest Austin growth corridor."),
    ("austin-taps", "Austin Taps", "Craft beer, breweries, and bars in Austin."),
    ("spurs-bench", "Spurs Bench", "Another corner for Spurs fan discussion."),
    ("sa-tables", "San Antonio Tables", "San Antonio restaurants and food news."),
    ("austin-rooms", "Austin Rooms", "Renting, buying, and housing in Austin."),
    ("austin-families", "Austin Families", "Parenting and family life in the Austin area."),
    ("austin-bands", "Austin Bands", "Musicians, venues, and live music scene in Austin."),
    ("bastrop", "Bastrop", "Bastrop and eastern Travis County."),
    ("austin-stages", "Austin Stages", "Live music listings, shows, and venue talk in Austin."),
]


def seed_hubs(db: Session) -> None:
    for slug, name, description in DEFAULT_HUBS:
        exists = db.query(Hub).filter(Hub.slug == slug).first()
        if not exists:
            db.add(Hub(slug=slug, name=name, description=description))
    db.commit()
