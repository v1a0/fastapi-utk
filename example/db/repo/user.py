from copy import deepcopy

from dto import User

from fastapi_utk import SortingOption


class UserRepo:
    fake_source = [
        User(1, 22, "Elliot", True),
        User(2, 44, "Mr. Robot", True),
        User(3, 44, "Angela", False),
        User(4, 22, "Darlene", True),
        User(5, 33, "Tyrell", False),
        User(6, 33, "Joanna", False),
        User(7, 22, "Gideon", False),
        User(8, 44, "Irving", True),
        User(9, 22, "Trenton", False),
        User(10, 22, "Mobley", False),
        User(11, 44, "Whiterose", False),
        User(12, 44, "Dom", True),
        User(13, 33, "Krista", True),
        User(14, 22, "Shayla", False),
        User(15, 33, "Vera", False),
        User(16, 22, "Leon", True),
        User(17, 22, "Phillip", False),
        User(18, 33, "Janice", False),
        User(19, 33, "Santiago", False),
        User(20, 44, "Susan", False),
        User(21, 44, "Olivia", False),
        User(22, 33, "Freddie", False),
        User(23, 22, "Magda", True),
        User(24, 44, "Fernando", False),
        User(25, 22, "Isaac", False),
        User(26, 22, "Colby", False),
        User(27, 22, "Angela Moss", False),
        User(28, 22, "Frank Cody", False),
        User(29, 22, "Lloyd", False),
        User(30, 22, "Cisco", False),
        User(31, 33, "Norma", False),
        User(32, 33, "Sun", False),
        User(33, 33, "Grant", False),
        User(34, 22, "Hamburger Man", False),
        User(35, 44, "Young Elliot", True),
        User(36, 22, "Marv", True),
        User(37, 22, "Bill Harper", True),
        User(38, 44, "Frankie", False),
        User(39, 33, "Julio", False),
        User(40, 22, "Berenice", False),
        User(41, 33, "Jack", False),
        User(42, 33, "Bo", False),
        User(43, 44, "Frank", False),
        User(44, 44, "Tyra", False),
        User(45, 33, "Jamie", False),
        User(46, 33, "Crystal", False),
        User(47, 22, "Norman", False),
        User(48, 44, "Lorenzo", False),
        User(49, 22, "Ray", False),
        User(50, 22, "Everett", False),
    ]

    @classmethod
    def get_users(
        cls,
        age: int | None = None,
        is_active: bool | None = None,
        _limit: int | None = None,
        _offset: int | None = None,
        _sort_by: list[SortingOption] | None = None,
    ) -> tuple[int, list[User]]:
        users = deepcopy(cls.fake_source)

        # filters
        if age is not None:
            users = [user for user in users if user.age == age]

        if is_active is not None:
            users = [user for user in users if user.is_active == is_active]

        total = len(users)

        # sorting
        if _sort_by:
            for sort_option in reversed(_sort_by):
                match sort_option.field:
                    case "id":
                        users = sorted(users, key=lambda user: user.id, reverse=sort_option.is_desc)
                    case "age":
                        users = sorted(
                            users,
                            key=lambda user: user.age,
                            reverse=sort_option.is_desc,
                        )
                    case "name":
                        users = sorted(
                            users,
                            key=lambda user: user.name,
                            reverse=sort_option.is_desc,
                        )
                    case "is_active":
                        users = sorted(
                            users,
                            key=lambda user: user.is_active,
                            reverse=sort_option.is_desc,
                        )
                    case _:
                        raise ValueError("Unknown sort option")

        # slicing
        if _offset is not None:
            users = users[_offset:]

        if _limit is not None:
            users = users[:_limit]

        return total, users
