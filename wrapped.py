#Utltimo scrape 10/12/2025

import pandas as pd
from collections import Counter
import re

pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)

df = pd.read_csv("ao3_stats_multi_page.csv", encoding="latin1")

df.columns = df.columns.str.replace("\ufeff", "", regex=True)
df.columns = df.columns.str.replace("ï»¿", "", regex=False)
df.columns = df.columns.str.strip()

df["times visited"] = (
    df["times visited"]
    .astype(str) 
    .str.replace(r"[^\d]", "", regex=True) 
)
df["visits_num"] = (
    df["times visited"]
    .replace("", "0") 
    .fillna("0")     
    .astype(int)
)



most_visited = df.loc[df["visits_num"].idxmax()]

total_fanfics = len(df)
total_words = df["words"].fillna(0).sum()
promedio_palabras = df["words"].fillna(0).mean()
mediana_palabras = df["words"].fillna(0).median()

top5 = df.sort_values(by="visits_num", ascending=False).head(10)


all_tags = []
for item in df["freeforms"].dropna():
    tags = [t.strip() for t in item.split(",")]
    all_tags.extend(tags)

counter = Counter(all_tags)


df["Fandoms_list"] = df["fandoms"].astype(str).str.split(",")

fandom_counts = df.explode("Fandoms_list")
fandom_counts["Fandoms_list"] = fandom_counts["Fandoms_list"].str.strip()
fandom_counts = fandom_counts[fandom_counts["Fandoms_list"] != ""]

fandom_summary = fandom_counts["Fandoms_list"].value_counts()
fandom_summary = fandom_summary[fandom_summary >= 5]

df["last visited"] = (
    df["last visited"]
    .astype(str)
    .str.replace("Last visited: ", "", regex=False)
    .str.strip()
)

df["last visited"] = pd.to_datetime(
    df["last visited"],
    format="%d %b %Y",
    errors="coerce"
)

df_2025 = df[df["last visited"].dt.year == 2025].copy()
df_2025["mes"] = df_2025["last visited"].dt.strftime("%b %Y")

reads_per_month = (
    df_2025["mes"]
    .value_counts()
    .sort_index(key=lambda x: pd.to_datetime(x, format="%b %Y"))
)

df["relationships_list"] = (
    df["relationships"]
    .fillna("")
    .apply(lambda x: [r.strip() for r in x.split(",") if r.strip()])
)

relationship_counts = (
    df.explode("relationships_list")["relationships_list"]
    .value_counts()
)

relationship_counts = relationship_counts[relationship_counts > 5]

df["rating_clean"] = df["rating"].fillna("Not Rated").str.strip()
rating_counts = df["rating_clean"].value_counts()
rating_percent = (rating_counts / len(df) * 100).round(2)

AU_KEYWORDS = [
    r"\bAU\b",
    r"\bAlternate Universe\b",
    r"\bAlternate-Universe\b",
    r"\bAlt Universe\b",
    r"\bcanon divergence\b",
    r"\bCanon-Divergence\b",
]

def extract_au(tag):
    t = tag.lower()

    if "au" not in t and "alternate" not in t:
        return None

    for kw in AU_KEYWORDS:
        if re.search(kw, tag, flags=re.IGNORECASE):
            return tag.strip()

    return None

freeforms_series = df.assign(
    freeforms_list=df["freeforms"].fillna("").astype(str).str.split(",")
).explode("freeforms_list")

freeforms_series["freeforms_list"] = freeforms_series["freeforms_list"].str.strip()
freeforms_series = freeforms_series[freeforms_series["freeforms_list"] != ""]

au_list = [extract_au(tag) for tag in freeforms_series["freeforms_list"] if extract_au(tag)]
au_counts = Counter(au_list)
au_counts = {au: c for au, c in sorted(au_counts.items(), key=lambda x: x[1], reverse=True) if c > 2}

print("=== AO3 WRAPPED ===")
print(f"Total de fanfics registrados: {total_fanfics}")
print(f"Total de palabras leídas: {total_words:,}")
print(f"Promedio de palabras por fanfic: {promedio_palabras:,.0f}")
print(f"Mediana de palabras por fanfic: {mediana_palabras:,.0f}")
print(f"Fanfic más visitado: {most_visited['title']} ({most_visited['times visited']} visitas)")

print("\n=== TOP 10 FANFICS MÁS VISITADOS ===")
print(top5[["title", "times visited"]])

print("\n=== TOP 20 TAGS MÁS LEÍDAS ===")
for tag, count in counter.most_common(20):
    print(f"{tag}: {count} veces")

print("\n=== LECTURAS POR MES (solo 2025) ===")
if len(reads_per_month) > 0:
    for mes, cant in reads_per_month.items():
        print(f"{mes}: {cant} fanfics")

    most_active_month = reads_per_month.idxmax()
    most_reads = reads_per_month.max()
    print(f"\nMes con más lecturas: {most_active_month} ({most_reads} fanfics)")
else:
    print("❗ No hay datos de 2025.")

print("\n=== RATING STATS ===")
for rating in rating_counts.index:
    print(f"{rating}: {rating_counts[rating]} fanfics ({rating_percent[rating]}%)")

print("\n=== RELATIONSHIPS MÁS LEÍDAS (más de 5 fanfics) ===")
for rel, count in relationship_counts.items():
    print(f"{rel}: {count}")

print("\n=== TOP AUs ===")
if len(au_counts) == 0:
    print("No se detectaron AUs.")
else:
    for au, count in au_counts.items():
        print(f"{au}: {count} fanfics")

print("\n=== FANDOMS LEÍDOS ===")
for fandom, num in fandom_summary.items():
    print(f"{fandom}: {num} fanfics")
