from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import Category, Flower, Order, OrderItem, Profile, Review


admin.site.site_header = "🌸 Flora Luxe Admin"
admin.site.site_title = "Flora Luxe"
admin.site.index_title = "Управление магазином"


# ─── PROFILE INLINE ───────────────────────────────────────────
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    fields = ['phone', 'address', 'avatar']
    extra = 0


# ─── USER ADMIN ───────────────────────────────────────────────
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'date_joined', 'user_actions')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('block/<int:user_id>/', self.admin_site.admin_view(self.block_user), name='auth_user_block'),
            path('unblock/<int:user_id>/', self.admin_site.admin_view(self.unblock_user), name='auth_user_unblock'),
        ]
        return custom_urls + urls

    def user_actions(self, obj):
        if obj.is_active:
            return format_html(
                '<a class="button" style="padding:2px 8px;background:#e74c3c;color:#fff;border-radius:4px;" href="{}">🔒 Блок</a>',
                reverse('admin:auth_user_block', args=[obj.id]),
            )
        return format_html(
            '<a class="button" style="padding:2px 8px;background:#27ae60;color:#fff;border-radius:4px;" href="{}">✅ Разблок</a>',
            reverse('admin:auth_user_unblock', args=[obj.id]),
        )
    user_actions.short_description = 'Действия'

    def block_user(self, request, user_id):
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.is_active = False
            user.save()
            messages.success(request, f'{user.username} заблокирован')
        return redirect('/admin/auth/user/')

    def unblock_user(self, request, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        messages.success(request, f'{user.username} разблокирован')
        return redirect('/admin/auth/user/')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ─── CATEGORY ─────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'flower_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def flower_count(self, obj):
        return obj.flowers.count()
    flower_count.short_description = 'Цветов'


# ─── FLOWER ───────────────────────────────────────────────────
@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ['flower_img', 'name', 'category', 'price_display', 'available', 'created_at']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']
    list_editable = ['available']
    list_per_page = 20

    def flower_img(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;">', obj.image.url)
        return '🌸'
    flower_img.short_description = ''

    def price_display(self, obj):
        return f"{obj.price:,} сум".replace(',', ' ')
    price_display.short_description = 'Цена'


# ─── ORDER ────────────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['flower', 'quantity', 'price']
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'receipt_code', 'user', 'status_badge', 'total_display', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['receipt_code', 'user__username', 'phone', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['receipt_code', 'created_at', 'updated_at', 'transaction_id']
    list_per_page = 25
    date_hierarchy = 'created_at'

    def status_badge(self, obj):
        colors = {
            'new': '#3498db',
            'processing': '#f39c12',
            'paid': '#27ae60',
            'delivered': '#2ecc71',
            'cancelled': '#e74c3c',
        }
        labels = {
            'new': 'Новый', 'processing': 'В обработке',
            'paid': 'Оплачен', 'delivered': 'Доставлен', 'cancelled': 'Отменён'
        }
        color = colors.get(obj.status, '#888')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:.78rem;font-weight:600;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Статус'

    def total_display(self, obj):
        return f"{obj.total_price:,} сум".replace(',', ' ')
    total_display.short_description = 'Сумма'


# ─── REVIEW ───────────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'flower', 'rating_stars', 'short_text', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    list_filter = ['is_approved', 'rating']
    search_fields = ['user__username', 'text']

    def rating_stars(self, obj):
        return '⭐' * obj.rating
    rating_stars.short_description = 'Оценка'

    def short_text(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    short_text.short_description = 'Текст'


# ─── PROFILE ──────────────────────────────────────────────────
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address_short']
    search_fields = ['user__username', 'phone']

    def address_short(self, obj):
        return obj.address[:40] + '...' if len(obj.address) > 40 else obj.address
    address_short.short_description = 'Адрес'
