from drf_yasg.utils import swagger_auto_schema


class AutoDocMixin:
    """ Миксин для автоматического добавления summary и description к методам ViewSet """

    # Маппинг summary
    summary_mapping = {
        'list': 'Получить список объектов',
        'create': 'Создать новый объект',
        'retrieve': 'Получить детали объекта',
        'partial_update': 'Частично обновить объект',
        'destroy': 'Удалить объект',
    }

    # Маппинг description
    description_mapping = {
        'list': 'Возвращает список всех объектов',
        'create': 'Создает новый объект с валидацией данных',
        'retrieve': 'Возвращает полную информацию об объекте по ID',
        'partial_update': 'Частично обновляет объект. Только указанные поля будут изменены',
        'destroy': 'Удаляет объект из базы данных',
    }

    def __init_subclass__(cls, **kwargs):
        """ Вызывается автоматически при создании подкласса """
        super().__init_subclass__(**kwargs)
        cls._apply_swagger_decorators()

    @classmethod
    def _apply_swagger_decorators(cls):
        """ Применяет swagger декораторы к методам класса """
        for action_name in cls.summary_mapping.keys():
            if hasattr(cls, action_name):
                method = getattr(cls, action_name)

                # Получаем summary и description
                summary = cls.summary_mapping.get(action_name)
                description = cls.description_mapping.get(action_name)

                # Создаем параметры для декоратора
                decorator_kwargs = {'operation_summary': summary}
                if description:
                    decorator_kwargs['operation_description'] = description

                # Применяем декоратор, только если метод еще не декорирован
                if not hasattr(method, '_swagger_auto_schema'):
                    decorated_method = swagger_auto_schema(**decorator_kwargs)(method)
                    setattr(cls, action_name, decorated_method)
