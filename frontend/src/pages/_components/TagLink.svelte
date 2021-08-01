<script>
  export let tagName
  function getUrl(name) {
    return `http://localhost:5000/questions/tags:${name}`
  }
</script>

<a href={getUrl(tagName)}>
  {tagName}
</a>
