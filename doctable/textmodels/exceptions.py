class DocTableExceptBase(Exception):
    def __init__(self):
        super().__init__(self.message)

class MissingSpacyPipelineComponent(DocTableExceptBase):
    message = 'Both the Spacy tagger and parser must be enabled to make a ParseTree.'

class TreeAlreadyAssigned(DocTableExceptBase):
    message = 'Current token already contains reference to a ParseTree.'

class PropertyNotAvailable(Exception):
    template = '{prop} is not available in Token because {parsefeatname} was not enabled while processing with Spacy.'
    def __init__(self, prop, parsefeatname):
        message = self.template.format(prop=prop, parsefeatname=parsefeatname)
        super().__init__(message)

