from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView, View
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress, Category
from .forms import CheckoutForm


class HomeView(ListView):
    model = Item
    paginate_by = 4
    template_name = 'home.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Нет активных товаров")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


def category_view(request, slug):
    category = Category.objects.get(slug=slug)
    product = Item.objects.all()
    item_of_category = Item.objects.filter(category=category)
    context = {
        'category': category,
        'item_of_category': item_of_category,
        'product': product
    }
    return render(request, 'item_list.html', context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            "form": form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: add redirect to the selected payment option
                return redirect('shop:checkout')
            messages.warning(self.request, 'Отмена заказа')
            return redirect('shop:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "Нет активных товаров")
            return redirect('shop:order-summary')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Количество товара было обновлено.')
            return redirect('shop:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, 'Этот товар был добавлен в вашу корзину.')
            return redirect('shop:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'Этот товар был добавлен в вашу корзину.')
        return redirect('shop:order-summary')

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, 'Этот товар был удален из вашей корзины.')
            return redirect('shop:order-summary')
        else:
            messages.info(request, 'Корзина товаров пуста.')
            return redirect('shop:product', slug=slug)
    else:
        messages.info(request, 'У вас нет активных заказов.')
        return redirect('shop:product', slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, 'Количество товара было обновлено.')
            return redirect('shop:order-summary')
        else:
            messages.info(request, 'Корзина товаров пуста.')
            return redirect('shop:product', slug=slug)
    else:
        messages.info(request, 'У вас нет активных заказов.')
        return redirect('shop:product', slug=slug)
