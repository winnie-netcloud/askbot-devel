import { writable } from 'svelte/store'

export default function persistentStore(storeName) {
  const { subscribe, set: setWritable } = writable({})

  function init() {
    const storedUser = window.localStorage.getItem(storeName)
    if (storedUser) {
      try {
        setWritable(JSON.parse(storedUser))
        return true
      } catch (error) {
        return false
      }
    }
    return false
  }

  function set(data) {
    setWritable(data)
    try {
      window.localStorage.setItem(storeName, JSON.stringify(data))
    } catch (error) {
      return false
    }
    return true
  }

  function empty() {
    setWritable({})
    window.localStorage.removeItem(storeName)
  }

  return {
    empty,
    init,
    subscribe,
    set
  }
}
