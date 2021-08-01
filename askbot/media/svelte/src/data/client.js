import ApolloClient from 'apollo-boost'
import fetch from 'node-fetch'

const client = new ApolloClient({
  uri: 'http://localhost.askbot.com:8000/gql/',
  fetch
})

export default client
