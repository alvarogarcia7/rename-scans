import dataclasses


@dataclasses.dataclass(frozen=True)
class MoveAction:
    old_path: str
    new_path: str

@dataclasses.dataclass
class MoveResult:
    returncode: int
    processed_files: int
    renames: list[MoveAction] = dataclasses.field(default_factory=list)
    messages: list[str] = dataclasses.field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.returncode == 0

