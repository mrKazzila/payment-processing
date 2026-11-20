from typing import ClassVar

from sqlalchemy import inspect


class ReprMixin:
    __repr_fields__: ClassVar[tuple[str, ...]] = ("id",)

    def __repr__(self) -> str:
        state = inspect(self, raiseerr=False)
        model_name = f"{type(self).__name__}"

        if state is None:
            return f"{model_name}(<unmapped>)"

        fields = (
            (
                f"{name}={state.dict[name]!r}"
                if name in state.dict
                else f"{name}=<unloaded>"
            )
            for name in self.__repr_fields__
        )

        return f"{model_name}({', '.join(fields)})"
