from backend.services.notion_service import NotionService


class TestFilterByDeepLevel:
    def test_get_characters_by_deep_level_npc_returns_redis_cache(
        self, mock_redis_service, mocker
    ):
        mock_characters = [
            {"properties": {"deeplevel": 3, "npc": False}},
            {"properties": {"deeplevel": 3, "npc": False}},
            {"properties": {"deeplevel": 3, "npc": False}},
            {"properties": {"deeplevel": 3, "npc": False}},
        ]
        mock_redis_service.query_characters_by_deep_status_npc.return_value = (
            mock_characters
        )
        mocker.patch.object(NotionService, "headcount", len(mock_characters))

        notion_service = NotionService()
        result = notion_service.get_characters_by_deep_level_npc_source("l3", False)

        assert result == mock_characters
        mock_redis_service.query_characters_by_deep_status_npc.assert_called_once_with(
            prefix="cryptids",
            deep_level="l3",
            npc=False,
        )

    def test_get_characters_by_deep_level_npc_empty_cache(
        self, mock_redis_service, mocker
    ):
        mock_redis_service.query_characters_by_deep_status_npc.return_value = []
        mocker.patch(
            "backend.services.notion_service.requests.post",
            return_value=mocker.MagicMock(
                raise_for_status=mocker.MagicMock(),
                json=mocker.MagicMock(return_value={"results": [], "has_more": False}),
            ),
        )

        notion_service = NotionService()
        result = notion_service.get_characters_by_deep_level_npc_source("l3", False)

        assert result == []
