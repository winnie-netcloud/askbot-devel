import gql from 'graphql-tag'

const SETTINGS_QUERY = gql`
  query settings {
    settings {
      appShortName
    }
  }
`

export default SETTINGS_QUERY
