import { I18N_URL } from '../config'
const LOADED_URLS = {}

function getCatalog() {
  if (!window.django) {
    window.django = {catalog: {}}
  }
  if (!window.django.catalog) {
    window.django.catalog = {}
  }
  return window.django.catalog
}

function setCatalog(catalog) {
  if (!window.django) {
    window.django = {}
  }
  window.django.catalog = catalog
}


function i18nStore () {

  async function loadCatalog(url) {
    // check if data was loaded
    if (LOADED_URLS[url]) return

    //if not, load the data, update the i18n catalog and mark url data as loaded
    const response = await fetch(`${I18N_URL}?route=${url}&package=askbot_frontend`)
    const data = await response.json()
    const catalog = getCatalog()
    setCatalog(Object.assign({}, catalog, data.catalog))
    LOADED_URLS[url] = true
  }

  return { loadCatalog }
}

export default i18nStore()
