#  Copyright (c) 2023 zfit
from __future__ import annotations

from typing import Tuple, Union, Optional

from typing import Literal

from pydantic import field_validator, model_validator, Field

from .serializer import BaseRepr
from ..core.space import Space
from ..util.exception import WorkInProgressError

NumericTyped = Union[float, int]

NameObsTyped = Optional[Union[Tuple[str], str]]


class SpaceRepr(BaseRepr):
    _implementation = Space
    hs3_type: Literal["Space"] = Field("Space", alias="type")
    name: str
    lower: Optional[NumericTyped] = Field(alias="min")
    upper: Optional[NumericTyped] = Field(alias="max")
    binning: Optional[float] = None  # TODO: binning

    @model_validator(mode="before")
    @classmethod
    def _validate_pre(cls, values):
        if cls.orm_mode(values):
            if values["n_obs"] > 1:
                raise RuntimeError(
                    "Multiple observables are not supported yet. For PDFs with multiple observables, "
                    "this should work. But directly dumping a multidimensional Space is not supported."
                )
            values = dict(values)
            values["name"] = values.pop("obs")[0]

        return values

    @field_validator("lower", mode="before")
    @classmethod
    def _validate_lower(cls, v):
        if cls.orm_mode(v):
            v = v[0, 0]
        return v

    @field_validator("upper", mode="before")
    @classmethod
    def _validate_upper(cls, v):
        if cls.orm_mode(v):
            v = v[0, 0]
        return v

    @field_validator("binning", mode="before")
    @classmethod
    def validate_binning(cls, v):
        if v is not None:
            raise WorkInProgressError("Binning is not implemented yet")
        return v

    def _to_orm(self, init) -> SpaceRepr._implementation:
        init["limits"] = init.pop("lower", None), init.pop("upper", None)
        init["obs"] = init.pop("name")
        init = super()._to_orm(init)
        return init
