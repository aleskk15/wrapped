(async function() {

  //=========AQUI CAMBIA TU INFORMACIO=========
  const usuarioAO3 = "TU_USUARIO_AO3";  
  const paginaInicio = 1;                
  const paginaFin = 10;
  //==========================================
  //no le muevas otra cosa ffs           

  const tipo = document.querySelector("#main.readings-index") ? "readings" :
               document.querySelector("#main.bookmarks-index") ? "bookmarks" :
               "works";

  let headers = "title,link,author,fandoms,category,relationships,characters,freeforms,rating,warnings,date,words,chapters,comments,kudos,bookmarks,hits,recipient,summary";
  if (tipo === "bookmarks")
    headers += ",bookmark tags,bookmark notes,bookmark user,bookmark date,bookmark url";
  if (tipo === "readings")
    headers += ",last visited,version,times visited";

  let csv = headers + "\n";
  const spacer = '\r\n';

  function getText(el, selector) {
    const x = el.querySelector(selector);
    return x ? x.textContent.trim() : "";
  }

  function getList(el, selector) {
    return Array.from(el.querySelectorAll(selector))
      .map(a => a.textContent.trim())
      .join(", ");
  }

  function escapeCsv(v) {
    if (Array.isArray(v)) {
      v = v.join(spacer).trim();
    }
    return `"${String(v).replace(/"/g, '""')}"`;
  }

  function getVisitedNodeValue(item) {
    const el = item.querySelector('.viewed.heading');
    return el && el.childNodes.length > 2 ? el.childNodes[2].nodeValue : null;
  }

  async function fetchAndParsePage(page) {
    const url = `https://archiveofourown.org/users/${usuarioAO3}/${tipo}?page=${page}`;
    console.log("Scrapeando:", url);

    const resp = await fetch(url, { credentials: "include" });
    const html = await resp.text();

    const doc = new DOMParser().parseFromString(html, "text/html");
    return Array.from(doc.querySelectorAll("li.work, li.bookmark"))
      .filter(li => !li.classList.contains("deleted"));
  }

  for (let p = paginaInicio; p <= paginaFin; p++) {
    const items = await fetchAndParsePage(p);

    for (const item of items) {
      const title = getText(item, "h4.heading > a:first-of-type");
      const url = "https://archiveofourown.org" + 
        (item.querySelector("h4.heading > a:first-of-type")?.getAttribute("href") || "");

      const author = getList(item, "h4.heading > a[rel=author]");
      const fandoms = getList(item, ".fandoms a");
      const category = getText(item, ".required-tags .category");
      const rating = getText(item, ".required-tags .rating .text");
      const warnings = getList(item, ".tags .warnings a");
      const relationships = getList(item, ".tags .relationships > a");
      const characters = getList(item, ".tags .characters > a");
      const freeforms = getList(item, ".tags .freeforms > a");

      const date = getText(item, ".header > .datetime");
      const words = getText(item, "dd.words").replace(/[^\d]/g, '');
      const chapters = '="' + getText(item, "dd.chapters") + '"';
      const comments = getText(item, "dd.comments").replace(/[^\d]/g, '');
      const kudos = getText(item, "dd.kudos").replace(/[^\d]/g, '');
      const bookmarks = getText(item, "dd.bookmarks").replace(/[^\d]/g, '');
      const hits = getText(item, "dd.hits").replace(/[^\d]/g, '');

      const summaryElements = Array.from(item.querySelectorAll('.summary > *'));
      const summary = summaryElements.map(n => n.textContent.trim()).join(' ').trim();

      const recipient = getList(item, "h4.heading > a[href$='gifts']");

      const fields = [
        title, url, author, fandoms, category, relationships, characters,
        freeforms, rating, warnings, date, words, chapters, comments,
        kudos, bookmarks, hits, recipient, summary
      ];

      if (tipo === "bookmarks") {
        const bookmark_tags = getList(item, ".user .tags a.tag");
        const notesElements = Array.from(item.querySelectorAll('.user .notes > *'));
        const bookmark_notes = notesElements.map(n => n.textContent.trim()).join(' ').trim();
        const bookmark_url = "https://archiveofourown.org/bookmarks/" + item.id.replace('bookmark_', '');
        const bookmark_user = getText(item, ".user .byline > a");
        const bookmark_date = getText(item, ".user .datetime");

        fields.push(bookmark_tags, bookmark_notes, bookmark_user, bookmark_date, bookmark_url);
      }

      if (tipo === "readings") {
        var visited = getVisitedNodeValue(item);

        let last_visited = "";
        let version = "";
        let times_visited = "";

        if (visited) {
          visited = visited.trim().replace(/\r\n|\n|\r/g, ' ');
          const visitedRegex = /^(.*?)\s*\((.*?)\)\s*(.*?)$/m; 
          const results = visited.match(visitedRegex);

          if (results) {
            last_visited = results[1].trim();
            version = results[2].trim();
            times_visited = results[3].trim();
          }
        }
        fields.push(last_visited, version, times_visited);
      }

      csv += fields.map(escapeCsv).join(',') + "\r\n";
    }
  }

  const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "ao3_stats_multi_page.csv";
  link.click();

  console.log("Scraping terminado. Archivo descargado.");
})();
