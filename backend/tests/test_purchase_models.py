"""Testes para os modelos de Compras."""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from modules.financial.models.goods_receipt import (
    GoodsReceipt,
    InspectionResult,
    ReceiptStatus,
    ReceiptType,
)
from modules.financial.models.product import Product, ProductStatus, ProductType, UnitOfMeasure
from modules.financial.models.product_category import (
    ProductCategory,
    ProductCategoryStatus,
    ProductCategoryType,
)
from modules.financial.models.purchase_approval import (
    ApprovalAction,
    ApprovalLevel,
    ApprovalStatus,
    ApprovalType,
    PurchaseApproval,
)
from modules.financial.models.purchase_order import (
    OrderPriority,
    OrderStatus,
    PurchaseOrder,
)
from modules.financial.models.purchase_quotation import (
    PaymentCondition,
    PurchaseQuotation,
    QuotationStatus,
)
from modules.financial.models.purchase_requisition import (
    PurchaseRequisition,
    RequisitionPriority,
    RequisitionStatus,
    RequisitionType,
)


class TestProductCategoryModel:
    """Testes para ProductCategory."""

    def test_create_product_category(self):
        """Testa criação de categoria de produto."""
        category = ProductCategory(
            condominio_id=uuid.uuid4(),
            code="MAT001",
            name="Materiais de Limpeza",
            description="Produtos de limpeza em geral",
            category_type=ProductCategoryType.MATERIAL.value,
            status=ProductCategoryStatus.ATIVA.value,
        )

        assert category.code == "MAT001"
        assert category.name == "Materiais de Limpeza"
        assert category.category_type == ProductCategoryType.MATERIAL.value
        assert category.status == ProductCategoryStatus.ATIVA.value

    def test_category_hierarchy(self):
        """Testa hierarquia de categorias."""
        parent = ProductCategory(
            id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            code="MAT",
            name="Materiais",
            category_type=ProductCategoryType.MATERIAL.value,
        )

        child = ProductCategory(
            condominio_id=parent.condominio_id,
            code="MAT001",
            name="Materiais de Limpeza",
            parent_id=parent.id,
            depth=1,
        )

        assert child.parent_id == parent.id
        assert child.depth == 1

    def test_category_types(self):
        """Testa todos os tipos de categoria."""
        types = [
            ProductCategoryType.MATERIAL,
            ProductCategoryType.SERVICO,
            ProductCategoryType.EQUIPAMENTO,
            ProductCategoryType.CONSUMIVEL,
            ProductCategoryType.PRODUTO,
        ]

        for t in types:
            category = ProductCategory(
                condominio_id=uuid.uuid4(),
                code="CAT",
                name="Categoria Teste",
                category_type=t.value,
            )
            assert category.category_type == t.value


class TestProductModel:
    """Testes para Product."""

    def test_create_product(self):
        """Testa criação de produto."""
        product = Product(
            condominio_id=uuid.uuid4(),
            code="PROD001",
            name="Detergente 500ml",
            description="Detergente neutro 500ml",
            product_type=ProductType.MATERIAL.value,
            unit_of_measure=UnitOfMeasure.UNIDADE.value,
            status=ProductStatus.ATIVO.value,
        )

        assert product.code == "PROD001"
        assert product.name == "Detergente 500ml"
        assert product.product_type == ProductType.MATERIAL.value
        assert product.unit_of_measure == UnitOfMeasure.UNIDADE.value
        assert product.status == ProductStatus.ATIVO.value

    def test_product_stock_tracking(self):
        """Testa controle de estoque do produto."""
        product = Product(
            condominio_id=uuid.uuid4(),
            code="PROD001",
            name="Detergente 500ml",
            track_stock=True,
            current_stock=Decimal("100"),
            minimum_stock=Decimal("10"),
            maximum_stock=Decimal("500"),
            reorder_point=Decimal("20"),
        )

        assert product.track_stock is True
        assert product.current_stock == Decimal("100")
        assert product.minimum_stock == Decimal("10")
        assert product.maximum_stock == Decimal("500")
        assert product.reorder_point == Decimal("20")

    def test_product_pricing(self):
        """Testa preços do produto."""
        product = Product(
            condominio_id=uuid.uuid4(),
            code="PROD001",
            name="Detergente 500ml",
            reference_price=Decimal("10.00"),
            last_purchase_price=Decimal("9.50"),
            average_price=Decimal("9.75"),
        )

        assert product.reference_price == Decimal("10.00")
        assert product.last_purchase_price == Decimal("9.50")
        assert product.average_price == Decimal("9.75")

    def test_update_price(self):
        """Testa atualização de preço."""
        product = Product(
            condominio_id=uuid.uuid4(),
            code="PROD001",
            name="Detergente 500ml",
            last_purchase_price=Decimal("9.50"),
            average_price=Decimal("9.50"),
            min_price=Decimal("9.50"),
            max_price=Decimal("9.50"),
            price_history=[],
        )

        product.update_price(Decimal("10.00"), "purchase")

        assert product.last_purchase_price == Decimal("10.00")
        assert len(product.price_history) == 1
        assert product.price_history[0]["price"] == "10.00"
        assert product.price_history[0]["source"] == "purchase"

    def test_block_product(self):
        """Testa bloqueio de produto."""
        product = Product(
            condominio_id=uuid.uuid4(),
            code="PROD001",
            name="Detergente 500ml",
            is_blocked=False,
            status=ProductStatus.ATIVO.value,
        )
        user_id = uuid.uuid4()

        product.block("Produto descontinuado", user_id)

        assert product.is_blocked is True
        assert product.block_reason == "Produto descontinuado"
        assert product.blocked_by == user_id
        assert product.blocked_at is not None
        assert product.status == ProductStatus.BLOQUEADO.value

    def test_unit_of_measure_types(self):
        """Testa todas as unidades de medida."""
        units = [
            UnitOfMeasure.UNIDADE,
            UnitOfMeasure.QUILOGRAMA,
            UnitOfMeasure.LITRO,
            UnitOfMeasure.METRO,
            UnitOfMeasure.METRO_QUADRADO,
            UnitOfMeasure.METRO_CUBICO,
            UnitOfMeasure.CAIXA,
            UnitOfMeasure.PACOTE,
            UnitOfMeasure.HORA,
            UnitOfMeasure.DIA,
            UnitOfMeasure.MES,
        ]

        for unit in units:
            product = Product(
                condominio_id=uuid.uuid4(),
                code="PROD",
                name="Produto Teste",
                unit_of_measure=unit.value,
            )
            assert product.unit_of_measure == unit.value


class TestPurchaseRequisitionModel:
    """Testes para PurchaseRequisition."""

    def test_create_requisition(self):
        """Testa criação de requisição."""
        requisition = PurchaseRequisition(
            condominio_id=uuid.uuid4(),
            number="REQ-2024-001",
            description="Compra de materiais de limpeza",
            requisition_type=RequisitionType.MATERIAL.value,
            priority=RequisitionPriority.MEDIA.value,
            status=RequisitionStatus.RASCUNHO.value,
            requisition_date=date.today(),
            requester_id=uuid.uuid4(),
        )

        assert requisition.number == "REQ-2024-001"
        assert requisition.description == "Compra de materiais de limpeza"
        assert requisition.status == RequisitionStatus.RASCUNHO.value
        assert requisition.priority == RequisitionPriority.MEDIA.value

    def test_submit_for_approval(self):
        """Testa submissão para aprovação."""
        requisition = PurchaseRequisition(
            condominio_id=uuid.uuid4(),
            number="REQ-2024-001",
            description="Compra de materiais",
            status=RequisitionStatus.RASCUNHO.value,
            requisition_date=date.today(),
            requester_id=uuid.uuid4(),
        )

        requisition.submit_for_approval()

        assert requisition.status == RequisitionStatus.PENDENTE_APROVACAO.value

    def test_approve_requisition(self):
        """Testa aprovação de requisição."""
        requisition = PurchaseRequisition(
            condominio_id=uuid.uuid4(),
            number="REQ-2024-001",
            description="Compra de materiais",
            status=RequisitionStatus.PENDENTE_APROVACAO.value,
            requisition_date=date.today(),
            requester_id=uuid.uuid4(),
        )
        approver_id = uuid.uuid4()

        requisition.approve(approver_id, "Aprovado")

        assert requisition.status == RequisitionStatus.APROVADA.value
        assert requisition.approved_by == approver_id
        assert requisition.approval_notes == "Aprovado"
        assert requisition.approval_date is not None

    def test_reject_requisition(self):
        """Testa rejeição de requisição."""
        requisition = PurchaseRequisition(
            condominio_id=uuid.uuid4(),
            number="REQ-2024-001",
            description="Compra de materiais",
            status=RequisitionStatus.PENDENTE_APROVACAO.value,
            requisition_date=date.today(),
            requester_id=uuid.uuid4(),
        )
        rejector_id = uuid.uuid4()

        requisition.reject(rejector_id, "Orçamento insuficiente")

        assert requisition.status == RequisitionStatus.REJEITADA.value
        assert requisition.rejected_by == rejector_id
        assert requisition.rejection_reason == "Orçamento insuficiente"

    def test_cancel_requisition(self):
        """Testa cancelamento de requisição."""
        requisition = PurchaseRequisition(
            condominio_id=uuid.uuid4(),
            number="REQ-2024-001",
            description="Compra de materiais",
            status=RequisitionStatus.RASCUNHO.value,
            requisition_date=date.today(),
            requester_id=uuid.uuid4(),
        )

        requisition.cancel("Não é mais necessário")

        assert requisition.status == RequisitionStatus.CANCELADA.value
        assert requisition.cancellation_reason == "Não é mais necessário"

    def test_start_quotation(self):
        """Testa início de cotação."""
        requisition = PurchaseRequisition(
            condominio_id=uuid.uuid4(),
            number="REQ-2024-001",
            description="Compra de materiais",
            status=RequisitionStatus.APROVADA.value,
            requisition_date=date.today(),
            requester_id=uuid.uuid4(),
        )

        requisition.start_quotation()

        assert requisition.status == RequisitionStatus.EM_COTACAO.value

    def test_requisition_priorities(self):
        """Testa todas as prioridades."""
        priorities = [
            RequisitionPriority.BAIXA,
            RequisitionPriority.MEDIA,
            RequisitionPriority.ALTA,
            RequisitionPriority.URGENTE,
            RequisitionPriority.CRITICA,
        ]

        for p in priorities:
            req = PurchaseRequisition(
                condominio_id=uuid.uuid4(),
                number="REQ",
                description="Teste",
                priority=p.value,
                requisition_date=date.today(),
                requester_id=uuid.uuid4(),
            )
            assert req.priority == p.value


class TestPurchaseQuotationModel:
    """Testes para PurchaseQuotation."""

    def test_create_quotation(self):
        """Testa criação de cotação."""
        quotation = PurchaseQuotation(
            condominio_id=uuid.uuid4(),
            number="COT-2024-001",
            supplier_id=uuid.uuid4(),
            status=QuotationStatus.SOLICITADA.value,
            quotation_date=date.today(),
            valid_until=date.today() + timedelta(days=30),
        )

        assert quotation.number == "COT-2024-001"
        assert quotation.status == QuotationStatus.SOLICITADA.value

    def test_receive_quotation(self):
        """Testa recebimento de cotação."""
        quotation = PurchaseQuotation(
            condominio_id=uuid.uuid4(),
            number="COT-2024-001",
            supplier_id=uuid.uuid4(),
            status=QuotationStatus.SOLICITADA.value,
            quotation_date=date.today(),
        )

        quotation.receive()

        assert quotation.status == QuotationStatus.RECEBIDA.value
        assert quotation.response_date is not None

    def test_set_scores(self):
        """Testa pontuação de cotação."""
        quotation = PurchaseQuotation(
            condominio_id=uuid.uuid4(),
            number="COT-2024-001",
            supplier_id=uuid.uuid4(),
            status=QuotationStatus.RECEBIDA.value,
            quotation_date=date.today(),
        )

        quotation.set_scores(
            Decimal("8.5"),
            Decimal("9.0"),
            Decimal("7.5"),
        )

        assert quotation.technical_score == Decimal("8.5")
        assert quotation.commercial_score == Decimal("9.0")
        assert quotation.delivery_score == Decimal("7.5")
        assert quotation.overall_score is not None
        assert quotation.status == QuotationStatus.EM_ANALISE.value

    def test_select_quotation(self):
        """Testa seleção de cotação."""
        quotation = PurchaseQuotation(
            condominio_id=uuid.uuid4(),
            number="COT-2024-001",
            supplier_id=uuid.uuid4(),
            status=QuotationStatus.EM_ANALISE.value,
            quotation_date=date.today(),
        )
        user_id = uuid.uuid4()

        quotation.select(user_id, "Melhor custo-benefício")

        assert quotation.is_selected is True
        assert quotation.selected_by == user_id
        assert quotation.selection_notes == "Melhor custo-benefício"
        assert quotation.status == QuotationStatus.SELECIONADA.value

    def test_reject_quotation(self):
        """Testa rejeição de cotação."""
        quotation = PurchaseQuotation(
            condominio_id=uuid.uuid4(),
            number="COT-2024-001",
            supplier_id=uuid.uuid4(),
            status=QuotationStatus.RECEBIDA.value,
            quotation_date=date.today(),
        )

        quotation.reject("Preço acima do mercado")

        assert quotation.status == QuotationStatus.REJEITADA.value
        assert quotation.rejection_reason == "Preço acima do mercado"

    def test_payment_conditions(self):
        """Testa condições de pagamento."""
        conditions = [
            PaymentCondition.A_VISTA,
            PaymentCondition.DIAS_7,
            PaymentCondition.DIAS_14,
            PaymentCondition.DIAS_21,
            PaymentCondition.DIAS_28,
            PaymentCondition.DIAS_30,
            PaymentCondition.DIAS_45,
            PaymentCondition.DIAS_60,
            PaymentCondition.DIAS_90,
            PaymentCondition.PARCELADO,
            PaymentCondition.A_VISTA,
        ]

        for c in conditions:
            quotation = PurchaseQuotation(
                condominio_id=uuid.uuid4(),
                number="COT",
                supplier_id=uuid.uuid4(),
                payment_condition=c.value,
                quotation_date=date.today(),
            )
            assert quotation.payment_condition == c.value


class TestPurchaseOrderModel:
    """Testes para PurchaseOrder."""

    def test_create_order(self):
        """Testa criação de ordem de compra."""
        order = PurchaseOrder(
            condominio_id=uuid.uuid4(),
            number="OC-2024-001",
            supplier_id=uuid.uuid4(),
            status=OrderStatus.RASCUNHO.value,
            priority=OrderPriority.NORMAL.value,
            order_date=date.today(),
        )

        assert order.number == "OC-2024-001"
        assert order.status == OrderStatus.RASCUNHO.value
        assert order.priority == OrderPriority.NORMAL.value
        assert order.revision == 1

    def test_submit_for_approval(self):
        """Testa submissão para aprovação."""
        order = PurchaseOrder(
            condominio_id=uuid.uuid4(),
            number="OC-2024-001",
            supplier_id=uuid.uuid4(),
            status=OrderStatus.RASCUNHO.value,
            order_date=date.today(),
        )

        order.submit_for_approval()

        assert order.status == OrderStatus.RASCUNHO.value

    def test_approve_order(self):
        """Testa aprovação de ordem."""
        order = PurchaseOrder(
            condominio_id=uuid.uuid4(),
            number="OC-2024-001",
            supplier_id=uuid.uuid4(),
            status=OrderStatus.RASCUNHO.value,
            order_date=date.today(),
        )
        approver_id = uuid.uuid4()

        order.approve(approver_id)

        assert order.status == OrderStatus.APROVADA.value
        assert order.approved_by == approver_id
        assert order.approval_date is not None

    def test_send_to_supplier(self):
        """Testa envio para fornecedor."""
        order = PurchaseOrder(
            condominio_id=uuid.uuid4(),
            number="OC-2024-001",
            supplier_id=uuid.uuid4(),
            status=OrderStatus.APROVADA.value,
            order_date=date.today(),
        )

        order.send_to_supplier()

        assert order.status == OrderStatus.RASCUNHO.value
        assert order.sent_date is not None

    def test_confirm_by_supplier(self):
        """Testa confirmação pelo fornecedor."""
        order = PurchaseOrder(
            condominio_id=uuid.uuid4(),
            number="OC-2024-001",
            supplier_id=uuid.uuid4(),
            status=OrderStatus.RASCUNHO.value,
            order_date=date.today(),
        )

        order.confirm_by_supplier("Pedido confirmado")

        assert order.status == OrderStatus.RASCUNHO.value
        assert order.confirmed_date is not None
        assert order.supplier_notes == "Pedido confirmado"

    def test_cancel_order(self):
        """Testa cancelamento de ordem."""
        order = PurchaseOrder(
            condominio_id=uuid.uuid4(),
            number="OC-2024-001",
            supplier_id=uuid.uuid4(),
            status=OrderStatus.RASCUNHO.value,
            order_date=date.today(),
        )

        order.cancel("Não é mais necessário")

        assert order.status == OrderStatus.CANCELADA.value
        assert order.cancellation_reason == "Não é mais necessário"

    def test_order_statuses(self):
        """Testa todos os status de ordem."""
        statuses = [
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.APROVADA,
            OrderStatus.REJEITADA,
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.RASCUNHO,
            OrderStatus.CANCELADA,
            OrderStatus.RASCUNHO,
        ]

        for s in statuses:
            order = PurchaseOrder(
                condominio_id=uuid.uuid4(),
                number="OC",
                supplier_id=uuid.uuid4(),
                status=s.value,
                order_date=date.today(),
            )
            assert order.status == s.value


class TestGoodsReceiptModel:
    """Testes para GoodsReceipt."""

    def test_create_receipt(self):
        """Testa criação de recebimento."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.PENDENTE.value,
            receipt_type=ReceiptType.NORMAL.value,
            receipt_date=date.today(),
        )

        assert receipt.number == "REC-2024-001"
        assert receipt.status == ReceiptStatus.PENDENTE.value
        assert receipt.receipt_type == ReceiptType.NORMAL.value

    def test_start_inspection(self):
        """Testa início de inspeção."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.PENDENTE.value,
            receipt_date=date.today(),
        )

        receipt.start_inspection()

        assert receipt.status == ReceiptStatus.EM_CONFERENCIA.value

    def test_complete_inspection(self):
        """Testa conclusão de inspeção."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.EM_CONFERENCIA.value,
            receipt_date=date.today(),
        )
        inspector_id = uuid.uuid4()

        receipt.complete_inspection(
            InspectionResult.APROVADO,
            inspector_id,
            "Materiais em conformidade",
        )

        assert receipt.status == ReceiptStatus.CONFERIDO.value
        assert receipt.inspection_result == InspectionResult.APROVADO.value
        assert receipt.inspected_by == inspector_id
        assert receipt.inspection_notes == "Materiais em conformidade"
        assert receipt.inspection_date is not None

    def test_approve_receipt(self):
        """Testa aprovação de recebimento."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.CONFERIDO.value,
            receipt_date=date.today(),
        )
        approver_id = uuid.uuid4()

        receipt.approve(approver_id)

        assert receipt.status == ReceiptStatus.APROVADO.value
        assert receipt.approved_by == approver_id
        assert receipt.approval_date is not None

    def test_reject_receipt(self):
        """Testa rejeição de recebimento."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.CONFERIDO.value,
            receipt_date=date.today(),
        )

        receipt.reject("Materiais danificados")

        assert receipt.status == ReceiptStatus.RECUSADO.value
        assert receipt.rejection_reason == "Materiais danificados"

    def test_register_divergence(self):
        """Testa registro de divergência."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.PENDENTE.value,
            receipt_date=date.today(),
            has_divergence=False,
        )

        receipt.register_divergence(
            "quantidade",
            "Quantidade recebida menor que solicitada",
            "solicitar_reposicao",
        )

        assert receipt.has_divergence is True
        assert receipt.divergence_type == "quantidade"
        assert receipt.divergence_description == "Quantidade recebida menor que solicitada"
        assert receipt.divergence_action == "solicitar_reposicao"
        assert receipt.status == ReceiptStatus.COM_DIVERGENCIA.value

    def test_sign_receipt(self):
        """Testa assinatura de recebimento."""
        receipt = GoodsReceipt(
            condominio_id=uuid.uuid4(),
            number="REC-2024-001",
            order_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            status=ReceiptStatus.APROVADO.value,
            receipt_date=date.today(),
        )

        receipt.sign("João Silva", "12345678900")

        assert receipt.receiver_name == "João Silva"
        assert receipt.receiver_document == "12345678900"
        assert receipt.received_at is not None


class TestPurchaseApprovalModel:
    """Testes para PurchaseApproval."""

    def test_create_approval(self):
        """Testa criação de aprovação."""
        approval = PurchaseApproval(
            condominio_id=uuid.uuid4(),
            approval_type=ApprovalType.REQUISICAO.value,
            document_id=uuid.uuid4(),
            document_number="REQ-001",
            approval_level=ApprovalLevel.SUPERVISOR.value,
            status=ApprovalStatus.PENDENTE.value,
            approver_id=uuid.uuid4(),
            requested_at=datetime.utcnow(),
        )

        assert approval.approval_type == ApprovalType.REQUISICAO.value
        assert approval.approval_level == ApprovalLevel.SUPERVISOR.value
        assert approval.status == ApprovalStatus.PENDENTE.value

    def test_approve_request(self):
        """Testa aprovação."""
        approval = PurchaseApproval(
            condominio_id=uuid.uuid4(),
            approval_type=ApprovalType.REQUISICAO.value,
            document_id=uuid.uuid4(),
            approval_level=ApprovalLevel.SUPERVISOR.value,
            status=ApprovalStatus.PENDENTE.value,
            approver_id=uuid.uuid4(),
            requested_at=datetime.utcnow(),
            action_history=[],
        )

        approval.approve("Aprovado conforme orçamento")

        assert approval.status == ApprovalStatus.APROVADO.value
        assert approval.action == ApprovalAction.APPROVE.value
        assert approval.comments == "Aprovado conforme orçamento"
        assert approval.responded_at is not None
        assert len(approval.action_history) == 1

    def test_reject_request(self):
        """Testa rejeição."""
        approval = PurchaseApproval(
            condominio_id=uuid.uuid4(),
            approval_type=ApprovalType.REQUISICAO.value,
            document_id=uuid.uuid4(),
            approval_level=ApprovalLevel.SUPERVISOR.value,
            status=ApprovalStatus.PENDENTE.value,
            approver_id=uuid.uuid4(),
            requested_at=datetime.utcnow(),
            action_history=[],
        )

        approval.reject("Orçamento insuficiente")

        assert approval.status == ApprovalStatus.REJEITADO.value
        assert approval.action == ApprovalAction.APPROVE.value
        assert approval.rejection_reason == "Orçamento insuficiente"

    def test_delegate_approval(self):
        """Testa delegação de aprovação."""
        original_approver = uuid.uuid4()
        new_approver = uuid.uuid4()
        delegator = uuid.uuid4()

        approval = PurchaseApproval(
            condominio_id=uuid.uuid4(),
            approval_type=ApprovalType.REQUISICAO.value,
            document_id=uuid.uuid4(),
            approval_level=ApprovalLevel.SUPERVISOR.value,
            status=ApprovalStatus.PENDENTE.value,
            approver_id=original_approver,
            requested_at=datetime.utcnow(),
            action_history=[],
        )

        approval.delegate(new_approver, delegator, "Ausência do aprovador original")

        assert approval.approver_id == new_approver
        assert approval.original_approver_id == original_approver
        assert approval.delegated_by == delegator
        assert approval.delegation_reason == "Ausência do aprovador original"
        assert approval.delegated_at is not None

    def test_request_info(self):
        """Testa solicitação de informações."""
        approval = PurchaseApproval(
            condominio_id=uuid.uuid4(),
            approval_type=ApprovalType.REQUISICAO.value,
            document_id=uuid.uuid4(),
            approval_level=ApprovalLevel.SUPERVISOR.value,
            status=ApprovalStatus.PENDENTE.value,
            approver_id=uuid.uuid4(),
            requested_at=datetime.utcnow(),
            action_history=[],
        )

        approval.request_info("Necessário justificativa detalhada")

        assert approval.status == ApprovalStatus.PENDENTE.value
        assert approval.info_requested == "Necessário justificativa detalhada"

    def test_provide_info(self):
        """Testa fornecimento de informações."""
        approval = PurchaseApproval(
            condominio_id=uuid.uuid4(),
            approval_type=ApprovalType.REQUISICAO.value,
            document_id=uuid.uuid4(),
            approval_level=ApprovalLevel.SUPERVISOR.value,
            status=ApprovalStatus.PENDENTE.value,
            approver_id=uuid.uuid4(),
            requested_at=datetime.utcnow(),
            info_requested="Necessário justificativa",
            action_history=[],
        )

        approval.provide_info("Compra necessária para manutenção preventiva")

        assert approval.status == ApprovalStatus.PENDENTE.value
        assert approval.info_provided == "Compra necessária para manutenção preventiva"

    def test_get_required_level(self):
        """Testa determinação de nível de aprovação."""
        assert PurchaseApproval.get_required_level(Decimal("500")) == ApprovalLevel.SUPERVISOR
        assert PurchaseApproval.get_required_level(Decimal("3000")) == ApprovalLevel.SUPERVISOR
        assert PurchaseApproval.get_required_level(Decimal("15000")) == ApprovalLevel.SUPERVISOR
        assert PurchaseApproval.get_required_level(Decimal("60000")) == ApprovalLevel.SUPERVISOR
        assert PurchaseApproval.get_required_level(Decimal("150000")) == ApprovalLevel.SUPERVISOR

    def test_approval_types(self):
        """Testa todos os tipos de aprovação."""
        types = [
            ApprovalType.REQUISICAO,
            ApprovalType.COTACAO,
            ApprovalType.ORDEM_COMPRA,
            ApprovalType.RECEBIMENTO,
            ApprovalType.PAGAMENTO,
        ]

        for t in types:
            approval = PurchaseApproval(
                condominio_id=uuid.uuid4(),
                approval_type=t.value,
                document_id=uuid.uuid4(),
                approval_level=ApprovalLevel.SUPERVISOR.value,
                approver_id=uuid.uuid4(),
                requested_at=datetime.utcnow(),
            )
            assert approval.approval_type == t.value
