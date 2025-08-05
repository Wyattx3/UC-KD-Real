from typing import Optional
from .base_role import BaseRole
from .villager_roles import (
    Lion, Owl, Turtle, Hunter, Monkey, Bat, Hedgehog,
    Deer, Giraffe, Buffalo, Cow, Sheep
)
from .predator_roles import (
    Leopard, Tiger, Jackal, WildBoar, Vulture, Crocodile
)
from .neutral_roles import Fox

class RoleFactory:
    def __init__(self):
        self.role_classes = {
            "lion": Lion,
            "leopard": Leopard,
            "tiger": Tiger,
            "jackal": Jackal,
            "fox": Fox,
            "turtle": Turtle,
            "vulture": Vulture,
            "monkey": Monkey,
            "owl": Owl,
            "crocodile": Crocodile,
            "deer": Deer,
            "giraffe": Giraffe,
            "buffalo": Buffalo,
            "cow": Cow,
            "sheep": Sheep,
            "bat": Bat,
            "hedgehog": Hedgehog,
            "wild_boar": WildBoar,
            "hunter": Hunter
        }
    
    def create_role(self, role_name: str) -> Optional[BaseRole]:
        role_class = self.role_classes.get(role_name.lower())
        if role_class:
            return role_class()
        return None
    
    def get_available_roles(self) -> list:
        return list(self.role_classes.keys())
    
    def is_valid_role(self, role_name: str) -> bool:
        return role_name.lower() in self.role_classes
