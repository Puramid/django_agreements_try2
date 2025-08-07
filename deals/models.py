# deals/models.py
from django.db import models
from django.utils import timezone


class CreditorType(models.IntegerChoices):
    BANK = 1, "Банк"
    MFKO = 2, "МФКО"
    MKO = 3, "МКО"


class Creditor(models.Model):
    id = models.AutoField(unique=True, primary_key=True, null=False, blank=False)
    type = models.IntegerField(
        "Тип кредитора", null=False, blank=False, choices=CreditorType.choices
    )
    name = models.CharField("Наименование", max_length=250, null=False, blank=False)

    date_add = models.DateTimeField("Дата создания", default=timezone.now)
    date_update = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        app_label = "deals"
        db_table = "credit_creditor"
        verbose_name_plural = "Кредитор"
        verbose_name = "кредитора"

    def __str__(self):
        return self.name


class AgreementTypes(models.IntegerChoices):
    CESS = 1, "Цессия"
    OUTS = 2, "Аутсорсинг"


class PortfolioTypes(models.IntegerChoices):
    CESS = 1, "Цессия"


class PortfolioProcessTypes(models.IntegerChoices):
    LEGAL = 1, "Лигал"
    IP = 2, "ИП"
    HARD = 3, "Хард"
    SOFT = 4, "Софт"
    SEIZE = 5, "Изъятие"
    BANKRUPT = 6, "Банкротство"
    FULL = 7, "Фулл"


class Agreement(models.Model):
    id = models.AutoField(primary_key=True)

    creditor = models.ForeignKey(
        Creditor,
        null=False,
        blank=False,
        related_name="creditor",
        verbose_name="Кредитор",
        on_delete=models.CASCADE,
    )

    creditor_first = models.ForeignKey(
        Creditor,
        null=True,
        blank=True,
        related_name="creditor_first",
        verbose_name="Первоначальный кредитор",
        on_delete=models.PROTECT,
    )

    agreement_code = models.CharField(
        "Реквизиты договора",
        max_length=250,
        blank=False,
        null=False,
    )

    agreement_date = models.DateTimeField(
        "Дата договора",
        blank=False,
    )

    agreement_type = models.PositiveSmallIntegerField(
        "Тип",
        choices=AgreementTypes.choices,
        default=AgreementTypes.CESS,
        editable=True,
    )

    date_add = models.DateTimeField(
        auto_now_add=True,
    )

    date_update = models.DateTimeField(
        auto_now=True,
    )

    total_sum = models.DecimalField(
        "Стоимость портфеля",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=False,
    )

    total_amount = models.DecimalField(
        "Размер портфеля",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=False,
    )

    def agreement_doc_path(self, filename):
        return f"agreements/{self.agreement_code}/{filename}"

    agreement_doc = models.FileField(
        verbose_name="Документ",
        upload_to=agreement_doc_path,
        max_length=1024,
        null=True,
    )

    class Meta:
        app_label = "deals"
        db_table = "agreement"
        verbose_name = "Договор"
        verbose_name_plural = "Договор"

    def __str__(self):
        return f"{self.agreement_code} ({self.get_agreement_type_display()})"


class Portfolio(models.Model):
    id = models.AutoField(
        unique=True,
        primary_key=True,
        null=False,
        blank=False,
    )

    date_add = models.DateTimeField(
        auto_now_add=True,
    )

    date_update = models.DateTimeField(
        auto_now=True,
    )

    label = models.CharField(
        "Наименование",
        max_length=250,
        blank=True,
        null=True,
    )

    type = models.PositiveSmallIntegerField(
        "Тип",
        choices=PortfolioTypes.choices,
        default=PortfolioTypes.CESS,
        editable=True,
    )

    process_type = models.PositiveSmallIntegerField(
        "Тип работы",
        choices=PortfolioProcessTypes.choices,
        default=PortfolioProcessTypes.LEGAL,
        editable=True,
    )

    agreement = models.ForeignKey(
        Agreement,
        null=False,
        blank=False,
        default=1,
        on_delete=models.CASCADE,
    )

    total_sum = models.DecimalField(
        "Стоимость",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=False,
    )

    date_placement = models.DateField(
        "дата начала работы",
        null=False,
        blank=False,
        default=timezone.now,
    )

    date_finish = models.DateField(
        "дата окончания работы",
        null=True,
        blank=True,
    )

    cession_date = models.DateField(
        "Дата переуступки",
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "deals"
        db_table = "credit_portfolio"
        verbose_name = "портфель"
        verbose_name_plural = "Портфель"

    def __str__(self):
        return self.label or "Без названия"

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = (
                f"{self.agreement.creditor}_"
                f"{self.agreement.get_agreement_type_display()}_"
                f"{self.date_placement.strftime('%d.%m.%Y')}_"
                f"{self.get_process_type_display()}"
            )
        super().save(*args, **kwargs)