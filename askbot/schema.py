import graphene
import graphql_jwt
from askbot.conf import settings as askbot_settings

class Settings(graphene.ObjectType):
    app_short_name = graphene.String()

    def resolve_app_short_name(self, info):
        return askbot_settings.APP_SHORT_NAME

class Query(graphene.ObjectType):
    settings = graphene.Field(Settings)

    def resolve_settings(self, info):
        return askbot_settings

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
