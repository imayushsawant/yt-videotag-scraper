"""
YouTube Video ID Word Generator

Generates meaningful English words and phrases that are exactly 11 characters long
(the length of a YouTube video ID) and checks if they correspond to real videos.

Two-tier approach:
  - Tier 1 (common words): curated list of everyday English words + names.
    These produce meaningful, human-readable combos like "GoodMorning", "HelloWorld".
  - Tier 2 (full dictionary): NLTK words corpus for broader coverage.
"""

import random
import string
from typing import Generator

# YouTube video IDs use: a-z, A-Z, 0-9, - , _
VALID_YT_CHARS = set(string.ascii_letters + string.digits + "-_")
TARGET_LENGTH = 11


# ── Curated common words ────────────────────────────────────────────────
COMMON_WORDS = [
    # 1-letter
    "i", "a",
    # 2-letter
    "am", "an", "as", "at", "be", "by", "do", "go", "he", "hi", "if",
    "in", "is", "it", "me", "my", "no", "of", "oh", "ok", "on", "or",
    "so", "to", "up", "us", "we",
    # 3-letter
    "ace", "act", "add", "age", "ago", "aid", "aim", "air", "all", "and",
    "any", "are", "arm", "art", "ask", "ate", "bad", "bag", "ban", "bar",
    "bat", "bay", "bed", "bet", "big", "bit", "bow", "box", "boy", "bug",
    "bus", "but", "buy", "cab", "can", "cap", "car", "cat", "cop", "cow",
    "cry", "cup", "cut", "dad", "dam", "day", "did", "die", "dig", "dim",
    "dip", "dog", "dot", "dry", "due", "ear", "eat", "egg", "end", "era",
    "eve", "eye", "fan", "far", "fat", "fed", "few", "fig", "fit", "fix",
    "fly", "for", "fox", "fun", "fur", "gap", "gas", "get", "god", "got",
    "gun", "gut", "guy", "had", "has", "hat", "her", "hid", "him", "hip",
    "his", "hit", "hot", "how", "hug", "ice", "ill", "ink", "inn", "ion",
    "its", "jam", "jar", "jaw", "jet", "job", "joy", "key", "kid", "kit",
    "lab", "lap", "law", "lay", "led", "leg", "let", "lid", "lie", "lip",
    "log", "lot", "low", "mad", "man", "map", "mat", "max", "may", "men",
    "met", "mid", "mix", "mob", "mom", "mud", "mug", "nap", "net", "new",
    "nil", "nor", "not", "now", "nut", "odd", "off", "oil", "old", "one",
    "ore", "our", "out", "owe", "own", "pad", "pan", "pay", "pen", "per",
    "pet", "pie", "pig", "pin", "pit", "pop", "pot", "pro", "pub",
    "put", "ran", "rat", "raw", "ray", "red", "rid", "rip", "rod", "row",
    "rub", "rug", "run", "sad", "sat", "saw", "say", "sea", "set", "she",
    "shy", "sin", "sir", "sit", "six", "ski", "sky", "son", "spy", "sum",
    "sun", "tab", "tag", "tap", "tax", "tea", "ten", "the", "tie", "tin",
    "tip", "toe", "ton", "too", "top", "toy", "try", "two", "use", "van",
    "via", "war", "was", "way", "web", "wet", "who", "why", "win", "wit",
    "won", "yes", "yet", "you", "zoo",
    # 4-letter
    "able", "also", "area", "army", "away", "back", "ball", "band", "bank",
    "base", "bath", "bean", "bear", "beat", "been", "beer", "bell", "belt",
    "bend", "best", "bill", "bird", "bite", "blow", "blue", "boat", "body",
    "bomb", "bond", "bone", "book", "boot", "born", "boss", "both", "bowl",
    "bulk", "burn", "busy", "cafe", "cage", "cake", "call", "calm", "came",
    "camp", "card", "care", "case", "cash", "cast", "cave", "chip", "city",
    "club", "clue", "coal", "coat", "code", "coin", "cold", "come", "cool",
    "cook", "cope", "copy", "core", "corn", "cost", "crew", "crop", "dark",
    "data", "date", "dawn", "dead", "deal", "dear", "debt", "deep", "deny",
    "desk", "diet", "dirt", "dish", "disk", "does", "done", "door", "dose",
    "down", "draw", "drop", "drug", "drum", "dual", "dull", "dump", "dust",
    "duty", "each", "earn", "ease", "east", "easy", "edge", "edit", "else",
    "emit", "epic", "even", "ever", "evil", "exam", "exit", "face", "fact",
    "fade", "fail", "fair", "fake", "fall", "fame", "farm", "fast", "fate",
    "fear", "feed", "feel", "feet", "fell", "felt", "file", "fill", "film",
    "find", "fine", "fire", "firm", "fish", "flag", "flat", "flow", "fold",
    "folk", "food", "fool", "foot", "ford", "form", "fort", "foul", "four",
    "free", "from", "fuel", "full", "fund", "fury", "gain", "game", "gang",
    "gate", "gave", "gear", "gene", "gift", "girl", "give", "glad", "glow",
    "glue", "goal", "goes", "gold", "golf", "gone", "good", "grab", "gray",
    "grew", "grey", "grid", "grip", "grow", "gulf", "guru", "guys", "hack",
    "hair", "half", "hall", "halt", "hand", "hang", "hard", "harm", "hate",
    "have", "head", "heal", "hear", "heat", "held", "help", "here", "hero",
    "hide", "high", "hill", "hint", "hire", "hold", "hole", "holy", "home",
    "hood", "hook", "hope", "horn", "host", "hour", "huge", "hung", "hunt",
    "hurt", "idea", "iron", "item", "jack", "joke", "jump", "jury", "just",
    "keen", "keep", "kept", "kick", "kill", "kind", "king", "kiss", "knee",
    "knew", "knit", "knot", "know", "lack", "lady", "laid", "lake", "lamp",
    "land", "lane", "last", "late", "lawn", "lead", "leaf", "lean", "left",
    "lend", "less", "life", "lift", "like", "limb", "lime", "line", "link",
    "lion", "list", "live", "load", "loan", "lock", "logo", "long", "look",
    "lord", "lose", "loss", "lost", "loud", "love", "luck", "lump", "lung",
    "made", "mail", "main", "make", "male", "mall", "many", "mark", "mass",
    "mate", "meal", "mean", "meat", "meet", "melt", "memo", "menu", "mere",
    "mild", "milk", "mill", "mind", "mine", "miss", "mode", "mood", "moon",
    "more", "most", "move", "much", "must", "myth", "nail", "name", "navy",
    "near", "neat", "neck", "need", "news", "next", "nice", "nine", "node",
    "none", "norm", "nose", "note", "noun", "obey", "odds", "okay", "once",
    "only", "onto", "open", "oral", "ours", "over", "pace", "pack", "page",
    "paid", "pain", "pair", "pale", "palm", "part", "pass", "past", "path",
    "peak", "pick", "pile", "pine", "pink", "pipe", "plan", "play", "plot",
    "plug", "plus", "poem", "poet", "pole", "poll", "pond", "pool", "poor",
    "pope", "pork", "port", "pose", "post", "pour", "pray", "pull", "pump",
    "pure", "push", "quit", "race", "rage", "raid", "rail", "rain", "rank",
    "rare", "rate", "read", "real", "rear", "rely", "rent", "rest", "rice",
    "rich", "ride", "ring", "rise", "risk", "road", "rock", "role", "roll",
    "roof", "room", "root", "rope", "rose", "ruin", "rule", "rush", "safe",
    "said", "sake", "sale", "salt", "same", "sand", "sang", "save", "seal",
    "seat", "seed", "seek", "seem", "seen", "self", "sell", "send", "sept",
    "ship", "shop", "shot", "show", "shut", "sick", "side", "sigh", "sign",
    "silk", "sing", "sink", "site", "size", "skin", "slam", "slip", "slow",
    "snap", "snow", "sock", "soft", "soil", "sold", "sole", "some", "song",
    "soon", "sort", "soul", "spin", "spot", "star", "stay", "stem", "step",
    "stir", "stop", "such", "suit", "sure", "swim", "tail", "take", "tale",
    "talk", "tall", "tank", "tape", "task", "taxi", "team", "tear", "tell",
    "temp", "tend", "tent", "term", "test", "text", "than", "that", "them",
    "then", "thin", "this", "thus", "tick", "tidy", "till", "time", "tiny",
    "tire", "told", "toll", "tone", "took", "tool", "tops", "tore", "torn",
    "tour", "town", "trap", "tree", "trim", "trip", "true", "tube", "tuck",
    "tune", "turn", "twin", "type", "ugly", "unit", "unto", "upon", "urge",
    "used", "user", "vain", "vast", "very", "vice", "view", "vine", "void",
    "volt", "vote", "wage", "wait", "wake", "walk", "wall", "want", "ward",
    "warm", "warn", "wash", "wave", "weak", "wear", "week", "well",
    "went", "were", "west", "what", "when", "whom", "wide", "wife", "wild",
    "will", "wind", "wine", "wing", "wire", "wise", "wish", "with", "wolf",
    "wood", "word", "wore", "work", "worm", "worn", "wrap", "yard", "yeah",
    "year", "your", "zero", "zone",
    # 5-letter
    "about", "above", "abuse", "adapt", "admit", "adopt", "adult", "after",
    "again", "agent", "agree", "ahead", "alarm", "album", "alien", "align",
    "alive", "allow", "alone", "along", "alter", "among", "angel", "anger",
    "angle", "angry", "apart", "apple", "apply", "arena", "argue", "arise",
    "aside", "asset", "await", "awake", "award", "aware", "awful", "basic",
    "basis", "beach", "begin", "being", "bench", "birth", "black", "blade",
    "blame", "blank", "blast", "blaze", "bleed", "blend", "blind", "block",
    "blood", "blown", "board", "bonus", "bound", "brain", "brand", "brave",
    "bread", "break", "breed", "brick", "brief", "bring", "broad", "broke",
    "brown", "brush", "build", "built", "burst", "buyer", "cabin", "carry",
    "catch", "cause", "chain", "chair", "charm", "chart", "chase", "cheap",
    "check", "cheek", "chess", "chest", "chief", "child", "china", "civil",
    "claim", "class", "clean", "clear", "climb", "cling", "clock", "close",
    "cloud", "coach", "coast", "color", "comet", "comic", "coral", "could",
    "count", "court", "cover", "crack", "craft", "crash", "crazy", "cream",
    "creek", "crime", "cross", "crowd", "crown", "cruel", "crush", "curve",
    "cycle", "daily", "dance", "debug", "delay", "dense", "depth", "devil",
    "dirty", "doubt", "dozen", "draft", "drain", "drama", "drank", "drawn",
    "dream", "dress", "drift", "drink", "drive", "drove", "dying", "eager",
    "early", "earth", "eight", "elect", "elite", "email", "empty", "enemy",
    "enjoy", "enter", "entry", "equal", "error", "essay", "event", "every",
    "exact", "exile", "exist", "extra", "faced", "faith", "false", "fancy",
    "fatal", "fault", "feast", "fence", "fewer", "fiber", "field", "fifth",
    "fifty", "fight", "final", "first", "fixed", "flame", "flash", "flesh",
    "float", "flood", "floor", "fluid", "flush", "focus", "force", "forge",
    "found", "frame", "fraud", "fresh", "front", "frost", "fruit", "fully",
    "funny", "genre", "ghost", "giant", "given", "glass", "globe", "gloom",
    "glory", "going", "grace", "grade", "grain", "grand", "grant", "graph",
    "grasp", "grass", "grave", "great", "green", "greet", "grief", "gross",
    "group", "grown", "guard", "guess", "guest", "guide", "guild", "guilt",
    "happy", "harsh", "haven", "heart", "heavy", "hello", "hence", "horse",
    "hotel", "house", "human", "humor", "hurry", "ideal", "image", "imply",
    "index", "indie", "inner", "input", "issue", "jewel", "joint", "judge",
    "juice", "knife", "knock", "known", "label", "large", "laser", "later",
    "laugh", "layer", "learn", "lease", "leave", "legal", "level", "light",
    "limit", "liner", "lemon", "local", "logic", "loose", "lover",
    "lower", "loyal", "lucky", "lunch", "lyric", "magic", "major", "maker",
    "march", "marry", "match", "maybe", "mayor", "media", "mercy", "merit",
    "metal", "meter", "might", "minor", "minus", "mixed", "model", "money",
    "month", "moral", "motor", "mount", "mouse", "mouth", "movie", "music",
    "naked", "nerve", "never", "night", "noble", "noise", "north", "noted",
    "novel", "nurse", "occur", "ocean", "offer", "often", "onion", "opera",
    "orbit", "order", "other", "ought", "outer", "owned", "owner", "oxide",
    "paint", "panel", "panic", "paper", "party", "patch", "pause", "peace",
    "pearl", "penny", "phase", "phone", "photo", "piano", "piece", "pilot",
    "pitch", "pixel", "pizza", "place", "plain", "plane", "plant", "plate",
    "plaza", "plead", "plumb", "point", "pound", "power", "press", "price",
    "pride", "prime", "print", "prior", "prize", "probe", "proof", "proud",
    "prove", "pulse", "punch", "pupil", "queen", "quest", "queue", "quick",
    "quiet", "quite", "quota", "quote", "radar", "radio", "raise", "range",
    "rapid", "ratio", "reach", "react", "ready", "realm", "rebel", "refer",
    "reign", "relax", "reply", "rider", "rifle", "right", "rival", "river",
    "robin", "robot", "roger", "rough", "round", "route", "royal",
    "rural", "salad", "sauce", "scale", "scene", "scope", "score", "sense",
    "serve", "seven", "shade", "shall", "shame", "shape", "share", "sharp",
    "sheep", "sheer", "sheet", "shelf", "shell", "shift", "shine", "shirt",
    "shock", "shoot", "shore", "short", "shout", "sight", "since", "sixth",
    "sixty", "skill", "slave", "sleep", "slide", "slope", "small", "smart",
    "smell", "smile", "smoke", "solar", "solve", "sorry", "sound", "south",
    "space", "spare", "spark", "speak", "speed", "spend", "spent", "spill",
    "spine", "split", "spoke", "sport", "spray", "squad", "stack", "staff",
    "stage", "stain", "stake", "stall", "stamp", "stand", "stark", "start",
    "state", "steal", "steam", "steel", "steep", "steer", "stick", "stiff",
    "still", "stock", "stone", "stood", "store", "storm", "story", "stove",
    "strip", "stuck", "study", "stuff", "style", "sugar", "suite", "super",
    "surge", "swamp", "swear", "sweep", "sweet", "swept", "swing", "sword",
    "swore", "sworn", "table", "taste", "teach", "their", "theme", "there",
    "these", "thick", "thing", "think", "third", "those", "three", "throw",
    "thumb", "tiger", "tight", "title", "today", "token", "topic", "total",
    "touch", "tough", "tower", "toxic", "trace", "track", "trade", "trail",
    "train", "trait", "trash", "treat", "trend", "trial", "tribe", "trick",
    "tried", "troop", "truck", "truly", "trump", "trunk", "trust", "truth",
    "twist", "ultra", "uncle", "under", "union", "unite", "unity", "until",
    "upper", "upset", "urban", "usage", "usual", "valid", "value", "verse",
    "video", "vigor", "virus", "visit", "vital", "vivid", "vocal", "voice",
    "voter", "waist", "waste", "watch", "water", "weigh", "weird", "wheat",
    "wheel", "where", "which", "while", "white", "whole", "whose", "woman",
    "women", "world", "worry", "worse", "worst", "worth", "would", "wound",
    "write", "wrong", "wrote", "yield", "young", "youth",
    # 6-letter
    "abroad", "absorb", "accept", "access", "across", "action", "actual",
    "adjust", "admire", "affirm", "afford", "agency", "agenda", "almost",
    "always", "amount", "animal", "annual", "answer", "anyone", "anyway",
    "appeal", "appear", "artist", "assume", "attack", "attend", "august",
    "barely", "basket", "battle", "beauty", "became", "become", "before",
    "behind", "belong", "beside", "beyond", "bishop", "bitter", "border",
    "borrow", "bottle", "bottom", "bounce", "branch", "breath", "bridge",
    "bright", "broken", "bronze", "budget", "bullet", "burden", "bureau",
    "butter", "button", "buying", "camera", "cancel", "carbon", "carpet",
    "castle", "caught", "center", "chance", "change", "charge", "cheese",
    "choice", "choose", "church", "circle", "closer", "coffee", "colony",
    "column", "combat", "comedy", "coming", "common", "cookie", "corner",
    "costly", "cotton", "county", "couple", "course", "cousin", "create",
    "credit", "crisis", "custom", "damage", "danger", "dealer", "debate",
    "decade", "decide", "defeat", "defend", "define", "degree", "demand",
    "denial", "depend", "deploy", "desert", "design", "desire", "detail",
    "detect", "device", "devote", "differ", "dinner", "direct", "divide",
    "doctor", "domain", "donate", "double", "dragon", "driver", "during",
    "easily", "eating", "editor", "effect", "effort", "eighth", "either",
    "emerge", "empire", "enable", "ending", "energy", "engage", "engine",
    "enough", "ensure", "entire", "equity", "escape", "estate", "ethnic",
    "evolve", "exceed", "except", "excuse", "expand", "expect", "expert",
    "export", "extend", "extent", "fabric", "facial", "factor", "fairly",
    "fallen", "family", "famous", "farmer", "father", "fellow",
    "female", "figure", "filter", "finger", "finish", "flight", "flower",
    "flying", "follow", "forest", "forget", "formal", "former", "fossil",
    "foster", "fourth", "freeze", "friend", "frozen", "future", "galaxy",
    "garden", "gather", "gazing", "gender", "gentle", "genius", "global",
    "golden", "govern", "ground", "growth", "guilty", "guitar", "handle",
    "hardly", "hassle", "hatred", "hazard", "health", "heaven", "height",
    "helped", "hereby", "hidden", "honest", "horror", "hunger", "hunter",
    "hustle", "ignore", "impact", "import", "impose", "income", "indeed",
    "indoor", "infant", "inform", "injure", "injury", "insect", "inside",
    "insist", "intact", "intend", "intent", "invest", "island", "itself",
    "jacket", "jersey", "jungle", "junior", "kidney", "killer", "kindly",
    "knight", "launch", "lawyer", "leader", "league", "legacy", "lender",
    "lesson", "letter", "lifted", "likely", "linear", "linger", "liquid",
    "listen", "little", "lively", "living", "lonely", "longer", "lovely",
    "luxury", "mainly", "manage", "manner", "marked", "market", "master",
    "matter", "medium", "member", "memory", "mental", "mentor", "merely",
    "method", "middle", "mighty", "minute", "mirror", "mobile", "modern",
    "modest", "modify", "moment", "monday", "monkey", "mostly", "mother",
    "motion", "murder", "museum", "mutual", "namely", "narrow", "nation",
    "nature", "nearby", "nearly", "nicely", "nobody", "normal", "notice",
    "notion", "number", "object", "obtain", "occupy", "offend", "office",
    "online", "oppose", "option", "oracle", "orange", "origin", "outlet",
    "output", "outset", "palace", "parent", "partly", "patrol", "patron",
    "people", "period", "permit", "person", "phrase", "planet", "player",
    "please", "pledge", "plenty", "pocket", "poetry", "poison", "police",
    "policy", "portal", "poster", "potato", "potent", "powder", "praise",
    "prayer", "prefer", "prince", "prison", "profit", "prompt", "proper",
    "proven", "public", "punish", "pursue", "puzzle", "racial", "random",
    "rarely", "rather", "rating", "reader", "really", "reason", "recall",
    "recent", "record", "reduce", "reform", "refuse", "regard", "regime",
    "region", "reject", "relate", "relief", "remain", "remedy", "remote",
    "remove", "render", "renew", "rental", "repair", "repeat", "report",
    "rescue", "resist", "resort", "result", "retail", "retain", "retire",
    "return", "reveal", "review", "revolt", "reward", "ribbon", "rising",
    "robust", "rocket", "ruling", "sacred", "safely", "safety",
    "salary", "sample", "saving", "scared", "scheme", "school", "screen",
    "script", "search", "season", "second", "secret", "sector", "secure",
    "seeker", "select", "seller", "senior", "series", "settle", "severe",
    "shadow", "shield", "shower", "signal", "silent", "silver", "simple",
    "simply", "singer", "single", "sister", "sketch", "slight", "smooth",
    "soccer", "social", "soften", "solely", "sought", "source", "speech",
    "sphere", "spirit", "spread", "spring", "square", "stable", "stance",
    "statue", "status", "steady", "strain", "strand", "stream", "street",
    "stress", "strict", "strike", "string", "strong", "studio", "submit",
    "sudden", "suffer", "summer", "summit", "supper", "supply", "surely",
    "survey", "switch", "symbol", "system", "tackle", "talent", "target",
    "temple", "tenant", "tender", "terror", "thanks", "threat", "throat",
    "throne", "timber", "tissue", "toward", "travel", "treaty", "tribal",
    "trophy", "tunnel", "twelve", "twenty", "unfair", "unfold", "unique",
    "united", "unlock", "unlike", "update", "uphold", "urgent", "useful",
    "valley", "varied", "vendor", "victim", "viewer", "virgin", "virtue",
    "vision", "volume", "wander", "warmth", "wealth", "weapon", "weekly",
    "wholly", "wicked", "widely", "window", "winner", "winter", "wisdom",
    "within", "wonder", "wooden", "worker", "worthy",
    # 7-letter
    "ability", "absence", "academy", "account", "achieve", "acquire",
    "address", "advance", "adverse", "analyst", "ancient", "anxiety",
    "anybody", "arrange", "article", "assault", "attempt", "attract",
    "auction", "average", "balance", "banking", "barrier", "battery",
    "bearing", "beating", "because", "brother", "cabinet", "captain",
    "capture", "careful", "caution", "ceiling", "central", "century",
    "certain", "chamber", "channel", "chapter", "charity", "chicken",
    "citizen", "climate", "closest", "cluster", "coastal", "collect",
    "college", "comfort", "command", "comment", "company", "compare",
    "compete", "complex", "compose", "concept", "concern", "conduct",
    "confirm", "connect", "consent", "consist", "contain", "content",
    "contest", "context", "control", "convert", "cooking", "correct",
    "council", "counter", "country", "courage", "current", "curtain",
    "dealing", "decline", "default", "defence", "deficit", "deliver",
    "density", "deposit", "deserts", "deserve", "digital", "display",
    "dispose", "distant", "diverse", "disturb", "drawing", "dynamic",
    "eastern", "economy", "edition", "educate", "elderly", "elegant",
    "element", "embrace", "emotion", "endless", "enforce", "engaged",
    "enhance", "essence", "evening", "evident", "examine", "example",
    "execute", "exhibit", "expense", "exploit", "explore", "express",
    "extreme", "factory", "faculty", "failure", "fantasy", "farming",
    "fashion", "feature", "fiction", "fighter", "finance", "fishing",
    "fitness", "foreign", "formula", "fortune", "forward", "founder",
    "fragile", "freedom", "fulfill", "furious", "gallery", "gateway",
    "general", "generic", "genuine", "gesture", "glimpse", "goddess",
    "granite", "graphic", "gravity", "grocery", "growing", "handful",
    "handler", "habitat", "harmony", "harvest", "heading", "hearing",
    "heating", "helpful", "highway", "history", "holding", "holiday",
    "horizon", "hostile", "housing", "hundred", "hunting", "husband",
    "imagine", "impress", "improve", "include", "initial", "inquiry",
    "insight", "inspect", "install", "instant", "instead", "interim",
    "invalid", "involve", "isolate", "journal", "journey",
    "justice", "justify", "keeping", "killing", "kitchen", "kingdom",
    "lacking", "landing", "lasting", "lateral", "lawsuit", "leading",
    "leather", "leaving", "lecture", "leisure", "lending", "liberal",
    "liberty", "license", "limited", "listing", "literal", "loading",
    "logical", "longest", "loyalty", "machine", "madness", "magical",
    "manager", "mansion", "meaning", "measure", "medical", "meeting",
    "mention", "message", "million", "mineral", "minimum", "miracle",
    "mission", "mixture", "monitor", "monster", "monthly", "morning",
    "mystery", "natural", "neither", "nervous", "neutral", "notable",
    "nothing", "nuclear", "nursing", "obvious", "offense", "officer",
    "ongoing", "opening", "operate", "opinion", "organic", "origins",
    "outdoor", "outline", "outlook", "outside", "overall", "overlap",
    "package", "painful", "parking", "partial", "partner",
    "passage", "passing", "passion", "patient", "pattern", "payment",
    "penalty", "pending", "pension", "percent", "perfect", "persist",
    "pioneer", "plastic", "playful", "pleased", "podcast",
    "popular", "portion", "poverty", "predict", "premium",
    "prepare", "present", "prevent", "primary", "printer", "privacy",
    "private", "problem", "proceed", "process", "produce", "product",
    "profile", "program", "project", "promise", "promote", "protect",
    "protein", "protest", "provide", "publish", "pursuit", "qualify",
    "quarter", "radical", "reality", "realize", "rebuild", "receipt",
    "receive", "recover", "recruit", "reflect", "refugee", "regular",
    "related", "release", "remains", "removal", "renewal", "replace",
    "request", "require", "reserve", "resolve", "respect", "respond",
    "restore", "retreat", "returns", "revenue", "revival", "revolve",
    "routine", "running", "satisfy", "scandal", "scatter", "scholar",
    "scratch", "section", "seeking", "segment", "serious", "service",
    "session", "setback", "setting", "seventh", "several", "shelter",
    "sheriff", "silence", "silicon", "similar", "sitting", "skilled",
    "slavery", "smoking", "society", "soldier", "someone", "special",
    "sponsor", "squeeze", "stadium", "startup", "station", "storage",
    "strange", "stretch", "student", "subject", "succeed", "success",
    "suggest", "summary", "sunrise", "support", "supreme", "surface",
    "surgeon", "surplus", "survive", "sustain", "teacher", "tension",
    "testing", "therapy", "thereby", "thought", "tobacco", "tonight",
    "torture", "totally", "tourism", "tourist", "towards", "tracker",
    "trading", "traffic", "tragedy", "trouble", "turning", "typical",
    "undergo", "unknown", "unusual", "updated", "upgrade", "variety",
    "vehicle", "venture", "version", "veteran", "victory",
    "violent", "virtual", "visible", "visitor", "waiting", "walking",
    "warfare", "warning", "warrior", "weather", "website", "wedding",
    "weekend", "welcome", "welfare", "western", "whisper", "willing",
    "winning", "witness", "workout", "writing", "written",
    # 8+ letter common words
    "absolute", "abstract", "academic", "accepted", "accident", "accurate",
    "actually", "addition", "adequate", "adjusted", "advanced", "advocate",
    "affected", "agreeing", "airplane", "alliance", "allowing", "although",
    "ambition", "analysis", "anything", "anywhere", "apparent", "applying",
    "approval", "arguably", "argument", "assembly", "assuming", "audience",
    "bachelor", "backward", "balanced", "baseball", "bathroom", "becoming",
    "behavior", "believed", "belonged", "birthday", "blessing",
    "blocking", "boundary", "breaking", "breeding", "briefing", "bringing",
    "brothers", "building", "business", "calendar", "campaign",
    "capacity", "casualty", "category", "cautious", "ceremony", "chairman",
    "champion", "changing", "charging", "chemical", "choosing", "children",
    "circular", "civilian", "clearing", "climbing", "clinical", "coaching",
    "collapse", "colonial", "combined", "comeback", "commerce",
    "commonly", "communal", "compared", "checking",
    "complete", "compound", "computer", "conclude", "concrete", "conflict",
    "confused", "congress", "conquest", "consider", "constant", "consumer",
    "continue", "contract", "contrast", "convince", "corridor", "covering",
    "coverage", "creation", "creative", "criminal", "critical", "crossing",
    "cultural", "currency", "customer", "database", "daughter", "deadline",
    "december", "deciding", "decision", "declared", "declined", "decrease",
    "defender", "definite", "delicate", "delivery", "democrat",
    "designer", "detailed", "detected", "dialogue", "directly",
    "director", "disabled", "disaster", "discount", "discover", "disorder",
    "disposal", "distance", "district", "division", "doctrine",
    "document", "domestic", "dominant", "donation", "doubtful", "dramatic",
    "duration", "dwelling", "earnings", "economic", "educated", "educator",
    "election", "electric", "elegance", "eligible", "embedded", "emerging",
    "emission", "emphasis", "employer", "enabling", "enclosed",
    "encoding", "enormous", "enrolled", "ensuring", "entering", "entirely",
    "entitled", "entrance", "envelope", "equality", "equipped", "estimate",
    "evaluate", "eventual", "everyday", "everyone", "evidence", "evolving",
    "exchange", "exciting", "excluded", "exercise",
    "existing", "expanded", "expected", "explicit", "explorer",
    "exposure", "extended", "external", "facility",
    "familiar", "farthest", "favorite", "featured", "february", "feedback",
    "feminine", "festival", "findings", "finished", "floating", "football",
    "forecast", "formerly", "founding", "fraction", "fragment",
    "friendly", "frontier", "function", "gambling", "generate", "genetics",
    "gorgeous", "governor", "graceful", "graduate", "graphics",
    "grateful", "guardian", "guidance", "gathered", "goodness", "handling",
    "happened", "hardware", "headline", "heritage", "homeland", "homeless",
    "homepage", "homework", "honestly", "horrible", "hospital", "humanity",
    "thousand", "together", "tomorrow", "treasure", "tropical",
    "possible", "positive",
    "football", "yourself", "powerful",
    "sandwich", "paradise", "anything", "whatever",
    "remember", "wonderful", "beautiful", "dangerous", "important",
    "different", "something", "sometimes", "everybody", "education",
    "structure", "community", "knowledge",
    "understand", "everything", "impossible", "government",
    "experience", "generation",
    # Names (common ones that are valid)
    "adam", "alex", "anna", "ayush", "brad", "carl", "dave", "emma",
    "eric", "evan", "fred", "greg", "hans", "jack", "jake", "jane",
    "jill", "john", "josh", "kate", "kyle", "liam", "lisa", "luke",
    "mark", "matt", "maya", "mike", "nick", "noah", "owen", "paul",
    "pete", "rosa", "ruby", "ryan", "sage", "sara", "sean", "seth",
    "theo", "todd", "tony", "wade", "zach", "zara",
]


def _get_common_words() -> list[str]:
    """Return deduplicated, filtered common words."""
    seen = set()
    result = []
    for w in COMMON_WORDS:
        wl = w.lower()
        if wl not in seen and all(c in VALID_YT_CHARS for c in wl):
            seen.add(wl)
            result.append(wl)
    return result


def _get_nltk_words() -> list[str]:
    """Load additional words from NLTK corpus (excluding common words)."""
    common = set(w.lower() for w in COMMON_WORDS)
    words = []
    try:
        import nltk
        try:
            from nltk.corpus import words as nltk_words
            raw = nltk_words.words()
        except LookupError:
            nltk.download("words", quiet=True)
            from nltk.corpus import words as nltk_words
            raw = nltk_words.words()

        seen = set()
        for w in raw:
            wl = w.lower()
            if (wl not in common
                    and wl not in seen
                    and len(wl) >= 3  # Skip 1-2 letter junk from NLTK
                    and all(c in VALID_YT_CHARS for c in wl)):
                seen.add(wl)
                words.append(wl)
    except ImportError:
        pass
    return words


def _build_length_index(words: list[str]) -> dict[int, list[str]]:
    """Index words by their length for fast lookup."""
    idx: dict[int, list[str]] = {}
    for w in words:
        length = len(w)
        if length <= TARGET_LENGTH:
            idx.setdefault(length, []).append(w)
    return idx


def _apply_casing(phrase: str) -> list[str]:
    """Generate different casing variants."""
    variants = set()
    variants.add(phrase)                       # alllowercase
    variants.add(phrase.capitalize())          # Firstupper
    variants.add(phrase.upper())               # ALLUPPER
    return list(variants)


def _apply_multi_word_casing(word_list: list[str]) -> list[str]:
    """Apply camelCase / PascalCase / mixed casing to multi-word combos."""
    variants = set()

    # all lowercase joined
    joined = "".join(word_list)
    variants.add(joined)

    # PascalCase (each word capitalized)
    pascal = "".join(w.capitalize() for w in word_list)
    variants.add(pascal)

    # camelCase (first word lower, rest capitalized)
    camel = word_list[0].lower() + "".join(w.capitalize() for w in word_list[1:])
    variants.add(camel)

    # ALL UPPER
    variants.add(joined.upper())

    return [v for v in variants if len(v) == TARGET_LENGTH]


# ── Generators ──────────────────────────────────────────────────────────

def generate_two_word_combos(length_index: dict[int, list[str]]) -> Generator[str, None, None]:
    """Generate two-word combinations that total 11 characters."""
    seen = set()

    for len1 in range(2, TARGET_LENGTH - 1):
        len2 = TARGET_LENGTH - len1
        words1 = list(length_index.get(len1, []))
        words2 = list(length_index.get(len2, []))

        if not words1 or not words2:
            continue

        random.shuffle(words1)
        random.shuffle(words2)

        for w1 in words1:
            for w2 in words2:
                for variant in _apply_multi_word_casing([w1, w2]):
                    if variant not in seen:
                        seen.add(variant)
                        yield variant


def generate_three_word_combos(length_index: dict[int, list[str]]) -> Generator[str, None, None]:
    """Generate three-word combinations that total 11 characters."""
    seen = set()

    for len1 in range(1, TARGET_LENGTH - 3):
        for len2 in range(2, TARGET_LENGTH - len1 - 1):
            len3 = TARGET_LENGTH - len1 - len2
            if len3 < 2:
                continue

            words1 = list(length_index.get(len1, []))
            words2 = list(length_index.get(len2, []))
            words3 = list(length_index.get(len3, []))

            if not words1 or not words2 or not words3:
                continue

            random.shuffle(words1)
            random.shuffle(words2)
            random.shuffle(words3)

            for w1 in words1[:80]:
                for w2 in words2[:40]:
                    for w3 in words3[:30]:
                        for variant in _apply_multi_word_casing([w1, w2, w3]):
                            if variant not in seen:
                                seen.add(variant)
                                yield variant


def generate_four_word_combos(length_index: dict[int, list[str]]) -> Generator[str, None, None]:
    """Generate four-word combinations that total 11 characters."""
    seen = set()

    for len1 in range(1, TARGET_LENGTH - 5):
        for len2 in range(2, TARGET_LENGTH - len1 - 3):
            for len3 in range(2, TARGET_LENGTH - len1 - len2 - 1):
                len4 = TARGET_LENGTH - len1 - len2 - len3
                if len4 < 2:
                    continue

                words1 = list(length_index.get(len1, []))
                words2 = list(length_index.get(len2, []))
                words3 = list(length_index.get(len3, []))
                words4 = list(length_index.get(len4, []))

                if not words1 or not words2 or not words3 or not words4:
                    continue

                random.shuffle(words1)
                random.shuffle(words2)
                random.shuffle(words3)
                random.shuffle(words4)

                for w1 in words1[:20]:
                    for w2 in words2[:15]:
                        for w3 in words3[:10]:
                            for w4 in words4[:8]:
                                for variant in _apply_multi_word_casing([w1, w2, w3, w4]):
                                    if variant not in seen:
                                        seen.add(variant)
                                        yield variant


def generate_single_words(length_index: dict[int, list[str]]) -> Generator[str, None, None]:
    """Generate single 11-letter words."""
    words_11 = list(length_index.get(TARGET_LENGTH, []))
    random.shuffle(words_11)
    for w in words_11:
        for variant in _apply_casing(w):
            if len(variant) == TARGET_LENGTH:
                yield variant


# ── Main entry point ────────────────────────────────────────────────────

def generate_candidates() -> Generator[str, None, None]:
    """
    Main generator that yields 11-character candidate strings
    made from meaningful English words / phrases.

    Priority order:
    1. Multi-word combos from COMMON words only (most meaningful)
    2. Single common 11-letter words
    3. Multi-word combos from full NLTK dictionary
    4. Single NLTK 11-letter words
    """
    # ── Phase 1: Common words only ──
    common_words = _get_common_words()
    common_index = _build_length_index(common_words)

    print(f"  Loaded {len(common_words)} common words")

    generators = [
        ("2-word", generate_two_word_combos(common_index)),
        ("3-word", generate_three_word_combos(common_index)),
        ("4-word", generate_four_word_combos(common_index)),
    ]

    exhausted = set()
    batch = 0
    while len(exhausted) < len(generators):
        batch += 1
        for name, gen in generators:
            if name in exhausted:
                continue
            count = 0
            batch_size = min(batch * 5, 30)
            try:
                while count < batch_size:
                    yield next(gen)
                    count += 1
            except StopIteration:
                exhausted.add(name)

    # Common single 11-letter words
    for candidate in generate_single_words(common_index):
        yield candidate

    # ── Phase 2: Full NLTK dictionary ──
    nltk_words = _get_nltk_words()
    if nltk_words:
        full_index = _build_length_index(common_words + nltk_words)
        print(f"  Expanding to full dictionary: {len(nltk_words)} additional words")

        for candidate in generate_two_word_combos(full_index):
            yield candidate

        for candidate in generate_single_words(full_index):
            yield candidate


if __name__ == "__main__":
    # Quick test
    count = 0
    for candidate in generate_candidates():
        print(f"  {candidate} (len={len(candidate)})")
        count += 1
        if count >= 30:
            break
