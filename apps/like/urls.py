from rest_framework.routers import SimpleRouter

from apps.like.views import LikeViewSet

router = SimpleRouter()

app_name = "likes"
router.register(r"likes", LikeViewSet, basename="likes")
urlpatterns = router.urls
