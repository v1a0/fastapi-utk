from dto import User


class UserRepo:
    fake_source = [
        User(1, 22, "Maksim"),
        User(2, 44, "Sasha"),
        User(3, 44, "Alex"),
        User(4, 22, "Dasha"),
        User(5, 33, "Leo"),
        User(6, 33, "Lena"),
        User(7, 22, "Roman"),
        User(8, 44, "Max"),
        User(9, 22, "Nick"),
        User(10, 22, "Oleg"),
        User(11, 44, "Sasha"),
        User(12, 44, "Anna"),
        User(13, 33, "Elena"),
        User(14, 22, "Eva"),
        User(15, 33, "Zoya"),
        User(16, 22, "Nina"),
        User(17, 22, "Vlad"),
        User(18, 33, "Mira"),
        User(19, 33, "Kate"),
        User(20, 44, "Nina"),
        User(21, 44, "Yana"),
        User(22, 33, "Kate"),
        User(23, 22, "Eva"),
        User(24, 44, "Dan"),
        User(25, 22, "Oleg"),
        User(26, 22, "Yana"),
        User(27, 22, "Ivan"),
        User(28, 22, "Kate"),
        User(29, 22, "Dasha"),
        User(30, 22, "Lena"),
        User(31, 33, "Pavel"),
        User(32, 33, "Anna"),
        User(33, 33, "Zoya"),
        User(34, 22, "Dasha"),
        User(35, 44, "Vlad"),
        User(36, 22, "Fedor"),
        User(37, 22, "Zoya"),
        User(38, 44, "Olga"),
        User(39, 33, "Dan"),
        User(40, 22, "Yana"),
        User(41, 33, "Oleg"),
        User(42, 33, "Sasha"),
        User(43, 44, "Leo"),
        User(44, 44, "Pavel"),
        User(45, 33, "Tim"),
        User(46, 33, "Fedor"),
        User(47, 22, "Dan"),
        User(48, 44, "John"),
        User(49, 22, "Tim"),
        User(50, 22, "Kate"),
    ]

    @classmethod
    def get_users(
        cls,
        age: int | None = None,
        _limit: int | None = None,
        _offset: int | None = None,
    ) -> tuple[int, list[User]]:
        global USERS

        users = list(cls.fake_source)

        if age is not None:
            users = [user for user in users if user.age == age]

        total = len(users)

        if _offset is not None:
            users = users[_offset:]

        if _limit is not None:
            users = users[:_limit]

        return total, users
