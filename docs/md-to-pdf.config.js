module.exports = {
  stylesheet: ["./docs/pdf-style.css"],
  pdf_options: {
    format: "A4",
    landscape: true,
    printBackground: true,
    displayHeaderFooter: true,
    margin: {
      top: "18mm",
      right: "12mm",
      bottom: "14mm",
      left: "12mm"
    },
    headerTemplate:
      '<div style="font-size:9px; width:100%; padding:0 10mm; color:#666; display:flex; justify-content:space-between;"><span>BioFrench Documentation</span><span class="date"></span></div>',
    footerTemplate:
      '<div style="font-size:9px; width:100%; padding:0 10mm; color:#666; display:flex; justify-content:flex-end;"><span class="pageNumber"></span>/<span class="totalPages"></span></div>'
  }
};
