from smarty.extensions import ma


class ContextSchema(ma.Schema):
    id = ma.Int(dump_only=True)
    context_type = ma.Nested('ContextTypeSchema')


class ContextTypeSchema(ma.Schema):
    id = ma.Int(dump_only=True)
    name = ma.Str()
    reproductions = ma.Nested('ActionSchema',
                              many=True,
                              exclude=("context_type", ))


class ActionSchema(ma.Schema):
    id = ma.Int(dump_only=True)
    type = ma.Method(serialize='get_type')
    content = ma.Str()
    image_name = ma.Str(missing='debian:stretch')
    context_type = ma.Nested(
        'ContextTypeSchema',
        exclude=("reproductions", ),
        dump_only=True,
    )

    def get_type(self, obj):
        return obj.type.name
