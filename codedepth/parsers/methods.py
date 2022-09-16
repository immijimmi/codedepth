class Decorators:
    @staticmethod
    def classproperty(func):
        class CustomDescriptor:
            def __get__(self, instance, owner):
                return func(owner)

            def __set__(self, instance, value):
                raise AttributeError("can't set attribute")

        return CustomDescriptor()
