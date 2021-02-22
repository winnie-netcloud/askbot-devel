<script>
  export let threads
</script>

<ul>
  {#if threads}
    {#each threads as thread}
      <li>{thread.title}</li>
    {/each}
  {/if}
</ul>
