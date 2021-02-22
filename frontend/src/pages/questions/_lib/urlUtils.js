const SEARCH_PARAMS = ['scope', 'sort', 'tags', 'author', 'page', 'page-size', 'query']

/**
 * Returns an object with key - as parameter name
 * and value - value of the parameter.
 * If the parameter name cannot be recognized,
 * returns an empty object.
 */
function getParam(slug) {
  const bits = slug.split(':')
  if (bits.length === 1) {
    return {}
  }

  const name = bits[0]
  if (SEARCH_PARAMS.includes(name)) {
    return {[name]: bits.slice(1).join(':')}
  }
  return {}
}

/** 
 * Returns a dictionary of question search parameters
 * ready to make the api call
 */
export function getSearchParams(slugs) {
  let searchParams = {}
  if (slugs.slug1) {
    searchParams = Object.assign({}, searchParams, getParam(slugs.slug1))
    if (slugs.slug2) {
      searchParams = Object.assign({}, searchParams, getParam(slugs.slug2))
      if (slugs.slug3) {
        searchParams = Object.assign({}, searchParams, getParam(slugs.slug3))
        if (slugs.slug4) {
          searchParams = Object.assign({}, searchParams, getParam(slugs.slug4))
          if (slugs.slug5) {
            searchParams = Object.assign({}, searchParams, getParam(slugs.slug5))
            if (slugs.slug6) {
              searchParams = Object.assign({}, searchParams, getParam(slugs.slug6))
              if (slugs.slug7) {
                searchParams = Object.assign({}, searchParams, getParam(slugs.slug7))
              }
            }
          }
        }
      }
    }
  }
  return searchParams
}

/**
 * Returns canonical url of the question search page
 */
export function getCanonicalUrl(params) {
  const bits = []
  SEARCH_PARAMS.forEach(name => {
    if (params[name]) {
      bits.push(`${name}:${params[name]}`)
    }
  })
  const path = bits.join('/')
  if (path) {
    return '/questions/' + path + '/'
  }
  return '/questions/'
}
