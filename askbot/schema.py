import graphene
from graphene import relay
import graphql_jwt
from askbot.conf import settings as askbot_settings

class Settings(graphene.ObjectType):
    app_short_name = graphene.String()
    authentication_page_message = graphene.String()

    class Meta:
        intefraces = (relay.Node,)

    def resolve_app_short_name(self, info):
        return askbot_settings.APP_SHORT_NAME

    def resolve_authentication_page_message(self, info):
        return askbot_settings.AUTHENTICATION_PAGE_MESSAGE

class Query(graphene.ObjectType):
    settings = graphene.Field(Settings)
    node = relay.Node.Field()

    def resolve_settings(self, info):
        return askbot_settings


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
