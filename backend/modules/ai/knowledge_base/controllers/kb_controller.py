"""
Knowledge Base Controller - Sprint 53.

Endpoints REST para base de conhecimento.
"""

import logging
import re
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database.session import get_db
from modules.ai.knowledge_base.repositories import KnowledgeBaseRepository
from modules.ai.knowledge_base.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
    FAQCreate,
    FAQListResponse,
    FAQResponse,
    FAQUpdate,
    KBCategoryCreate,
    KBCategoryResponse,
    KnowledgeBaseCreate,
    KnowledgeBaseDashboard,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    QAAnswerResponse,
    QAFeedbackRequest,
    QAQuestionRequest,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from modules.ai.knowledge_base.services import (
    ArticleGenerator,
    QAEngine,
    SemanticSearchEngine,
)

logger = logging.getLogger(__name__)

kb_router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


def generate_slug(text: str) -> str:
    """Gera slug a partir do texto."""
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:100]


# =============================================================================
# Knowledge Base Endpoints
# =============================================================================


@kb_router.post("/", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Cria nova base de conhecimento."""
    repo = KnowledgeBaseRepository(db)

    slug = data.slug or generate_slug(data.name)

    # Verifica se slug ja existe
    existing = repo.get_knowledge_base_by_slug(slug)
    if existing:
        slug = f"{slug}-{str(uuid4())[:8]}"

    kb = repo.create_knowledge_base(
        name=data.name,
        slug=slug,
        description=data.description,
        kb_type=data.kb_type.value,
        visibility=data.visibility.value,
        condominio_id=data.condominio_id,
        settings=data.settings,
    )

    return kb


@kb_router.get("/", response_model=list[KnowledgeBaseListResponse])
async def list_knowledge_bases(
    condominio_id: UUID | None = None,
    status: str | None = None,
    kb_type: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Lista bases de conhecimento."""
    repo = KnowledgeBaseRepository(db)
    items, _ = repo.list_knowledge_bases(
        condominio_id=condominio_id,
        status=status,
        kb_type=kb_type,
        skip=skip,
        limit=limit,
    )
    return items


@kb_router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Busca base de conhecimento por ID."""
    repo = KnowledgeBaseRepository(db)
    kb = repo.get_knowledge_base(kb_id)

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )

    return kb


@kb_router.patch("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: UUID,
    data: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Atualiza base de conhecimento."""
    repo = KnowledgeBaseRepository(db)

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value
    if "visibility" in update_data and update_data["visibility"]:
        update_data["visibility"] = update_data["visibility"].value
    if "kb_type" in update_data and update_data["kb_type"]:
        update_data["kb_type"] = update_data["kb_type"].value

    kb = repo.update_knowledge_base(kb_id, **update_data)

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )

    return kb


@kb_router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Remove base de conhecimento."""
    repo = KnowledgeBaseRepository(db)

    if not repo.delete_knowledge_base(kb_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )


# =============================================================================
# Category Endpoints
# =============================================================================


@kb_router.post("/{kb_id}/categories", response_model=KBCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    kb_id: UUID,
    data: KBCategoryCreate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Cria nova categoria."""
    repo = KnowledgeBaseRepository(db)

    slug = data.slug or generate_slug(data.name)

    category = repo.create_category(
        knowledge_base_id=kb_id,
        name=data.name,
        slug=slug,
        description=data.description,
        parent_id=data.parent_id,
        icon=data.icon,
        color=data.color,
        order=data.order,
    )

    return category


@kb_router.get("/{kb_id}/categories", response_model=list[KBCategoryResponse])
async def list_categories(
    kb_id: UUID,
    parent_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Lista categorias de uma KB."""
    repo = KnowledgeBaseRepository(db)
    return repo.list_categories(kb_id, parent_id)


# =============================================================================
# Article Endpoints
# =============================================================================


@kb_router.post("/{kb_id}/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    kb_id: UUID,
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Cria novo artigo."""
    repo = KnowledgeBaseRepository(db)

    slug = data.slug or generate_slug(data.title)

    article = repo.create_article(
        knowledge_base_id=kb_id,
        title=data.title,
        slug=slug,
        content=data.content,
        article_type=data.article_type.value,
        category_id=data.category_id,
        tags=data.tags,
        keywords=data.keywords,
        metadata=data.metadata,
    )

    return article


@kb_router.get("/{kb_id}/articles", response_model=list[ArticleListResponse])
async def list_articles(
    kb_id: UUID,
    category_id: UUID | None = None,
    status: str | None = None,
    article_type: str | None = None,
    search: str | None = None,
    tags: list[str] | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Lista artigos."""
    repo = KnowledgeBaseRepository(db)
    items, _ = repo.list_articles(
        knowledge_base_id=kb_id,
        category_id=category_id,
        status=status,
        article_type=article_type,
        tags=tags,
        search=search,
        skip=skip,
        limit=limit,
    )
    return items


@kb_router.get("/{kb_id}/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    kb_id: UUID,
    article_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Busca artigo por ID."""
    repo = KnowledgeBaseRepository(db)
    article = repo.get_article(article_id)

    if not article or str(article.knowledge_base_id) != str(kb_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    # Incrementa view
    repo.increment_article_view(article_id)

    return article


@kb_router.patch("/{kb_id}/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    kb_id: UUID,
    article_id: UUID,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Atualiza artigo."""
    repo = KnowledgeBaseRepository(db)

    update_data = data.model_dump(exclude_unset=True)
    if "article_type" in update_data and update_data["article_type"]:
        update_data["article_type"] = update_data["article_type"].value
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    article = repo.update_article(article_id, **update_data)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


@kb_router.post("/{kb_id}/articles/{article_id}/feedback")
async def add_article_feedback(
    kb_id: UUID,
    article_id: UUID,
    is_helpful: bool | None = None,
    rating: int | None = Query(None, ge=1, le=5),
    comment: str | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Adiciona feedback ao artigo."""
    repo = KnowledgeBaseRepository(db)

    feedback = repo.add_article_feedback(
        article_id=article_id,
        is_helpful=is_helpful,
        rating=rating,
        comment=comment,
    )

    return {"success": True, "feedback_id": str(feedback.id)}


# =============================================================================
# FAQ Endpoints
# =============================================================================


@kb_router.post("/{kb_id}/faqs", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    kb_id: UUID,
    data: FAQCreate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Cria nova FAQ."""
    repo = KnowledgeBaseRepository(db)

    faq = repo.create_faq(
        knowledge_base_id=kb_id,
        question=data.question,
        answer=data.answer,
        source=data.source.value,
        category_id=data.category_id,
        tags=data.tags,
        keywords=data.keywords,
        question_variations=data.question_variations,
        metadata=data.metadata,
    )

    return faq


@kb_router.get("/{kb_id}/faqs", response_model=list[FAQListResponse])
async def list_faqs(
    kb_id: UUID,
    category_id: UUID | None = None,
    status: str | None = None,
    search: str | None = None,
    tags: list[str] | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Lista FAQs."""
    repo = KnowledgeBaseRepository(db)
    items, _ = repo.list_faqs(
        knowledge_base_id=kb_id,
        category_id=category_id,
        status=status,
        tags=tags,
        search=search,
        skip=skip,
        limit=limit,
    )
    return items


@kb_router.get("/{kb_id}/faqs/{faq_id}", response_model=FAQResponse)
async def get_faq(
    kb_id: UUID,
    faq_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Busca FAQ por ID."""
    repo = KnowledgeBaseRepository(db)
    faq = repo.get_faq(faq_id)

    if not faq or str(faq.knowledge_base_id) != str(kb_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )

    # Incrementa view
    repo.increment_faq_view(faq_id)

    return faq


@kb_router.patch("/{kb_id}/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(
    kb_id: UUID,
    faq_id: UUID,
    data: FAQUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Atualiza FAQ."""
    repo = KnowledgeBaseRepository(db)

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    faq = repo.update_faq(faq_id, **update_data)

    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )

    return faq


@kb_router.post("/{kb_id}/faqs/{faq_id}/feedback")
async def add_faq_feedback(
    kb_id: UUID,
    faq_id: UUID,
    is_helpful: bool | None = None,
    rating: int | None = Query(None, ge=1, le=5),
    comment: str | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Adiciona feedback a FAQ."""
    repo = KnowledgeBaseRepository(db)

    feedback = repo.add_faq_feedback(
        faq_id=faq_id,
        is_helpful=is_helpful,
        rating=rating,
        comment=comment,
    )

    return {"success": True, "feedback_id": str(feedback.id)}


# =============================================================================
# Search Endpoints
# =============================================================================


@kb_router.post("/{kb_id}/search", response_model=SemanticSearchResponse)
async def search_knowledge_base(
    kb_id: UUID,
    data: SemanticSearchRequest,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Busca semantica na base de conhecimento."""
    repo = KnowledgeBaseRepository(db)
    search_engine = SemanticSearchEngine()

    # Busca artigos
    articles = []
    if data.include_articles:
        article_list, _ = repo.list_articles(
            knowledge_base_id=kb_id,
            status="published",
            limit=100,
        )
        for a in article_list:
            articles.append(
                {
                    "id": str(a.id),
                    "title": a.title,
                    "content": a.content,
                    "excerpt": a.excerpt,
                    "article_type": a.article_type,
                    "keywords": a.keywords,
                    "embedding": a.embedding,
                }
            )

    # Busca FAQs
    faqs = []
    if data.include_faqs:
        faq_list, _ = repo.list_faqs(
            knowledge_base_id=kb_id,
            status="published",
            limit=100,
        )
        for f in faq_list:
            faqs.append(
                {
                    "id": str(f.id),
                    "title": f.question,
                    "content": f"{f.question} {f.answer}",
                    "question": f.question,
                    "answer_short": f.answer_short,
                    "keywords": f.keywords,
                    "embedding": f.question_embedding,
                }
            )

    # Combina documentos
    all_docs = []
    for a in articles:
        a["type"] = "article"
        all_docs.append(a)
    for f in faqs:
        f["type"] = "faq"
        all_docs.append(f)

    # Executa busca
    results = search_engine.search(
        query=data.query,
        documents=all_docs,
        search_type=data.search_type,
        max_results=data.max_results,
        min_score=data.min_score,
    )

    # Separa resultados
    article_results = []
    faq_results = []

    for r in results:
        doc = r["document"]
        if doc.get("type") == "article":
            article_results.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "excerpt": doc.get("excerpt"),
                    "article_type": doc.get("article_type"),
                    "relevance_score": r["final_score"],
                    "matched_keywords": r.get("matched_keywords", []),
                    "highlights": r.get("highlights", []),
                }
            )
        else:
            faq_results.append(
                {
                    "id": doc["id"],
                    "question": doc.get("question"),
                    "answer_short": doc.get("answer_short"),
                    "relevance_score": r["final_score"],
                    "confidence": r["final_score"],
                    "matched_variation": None,
                }
            )

    return {
        "query": data.query,
        "total_results": len(results),
        "articles": article_results,
        "faqs": faq_results,
        "suggestions": [],
        "related_queries": [],
        "processing_time_ms": 0,
    }


# =============================================================================
# Q&A Endpoints
# =============================================================================


@kb_router.post("/{kb_id}/ask", response_model=QAAnswerResponse)
async def ask_question(
    kb_id: UUID,
    data: QAQuestionRequest,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Faz uma pergunta e recebe resposta da IA."""
    repo = KnowledgeBaseRepository(db)
    qa_engine = QAEngine()

    # Cria ou recupera sessao
    session_id = data.session_id
    if not session_id:
        session_key = f"qa-{uuid4()}"
        session = repo.create_qa_session(
            session_key=session_key,
            knowledge_base_id=kb_id,
            context=data.context,
        )
        session_id = session.id

    # Busca artigos e FAQs
    articles = []
    article_list, _ = repo.list_articles(
        knowledge_base_id=kb_id,
        status="published",
        limit=50,
    )
    for a in article_list:
        articles.append(
            {
                "id": str(a.id),
                "title": a.title,
                "content": a.content,
                "excerpt": a.excerpt,
                "summary": a.summary,
                "article_type": a.article_type,
                "keywords": a.keywords,
                "embedding": a.embedding,
            }
        )

    faqs = []
    faq_list, _ = repo.list_faqs(
        knowledge_base_id=kb_id,
        status="published",
        limit=50,
    )
    for f in faq_list:
        faqs.append(
            {
                "id": str(f.id),
                "question": f.question,
                "answer": f.answer,
                "answer_short": f.answer_short,
                "keywords": f.keywords,
                "question_embedding": f.question_embedding,
            }
        )

    # Processa pergunta
    result = qa_engine.process_question(
        question=data.question,
        articles=articles,
        faqs=faqs,
        context=data.context,
    )

    # Salva interacao
    interaction = repo.add_qa_interaction(
        session_id=session_id,
        question=data.question,
        response_type=result["response_type"],
        response=result["answer"],
        confidence_score=result["confidence_score"],
        matched_articles=result.get("matched_articles", []),
        matched_faqs=result.get("matched_faqs", []),
        response_time_ms=result["processing_time_ms"],
    )

    return {
        "session_id": session_id,
        "interaction_id": interaction.id,
        "question": data.question,
        "answer": result["answer"],
        "answer_formatted": result["answer_formatted"],
        "response_type": result["response_type"],
        "confidence_score": result["confidence_score"],
        "sources": result.get("sources", []),
        "matched_faqs": result.get("matched_faqs", []),
        "matched_articles": result.get("matched_articles", []),
        "suggestions": result.get("suggestions", []),
        "follow_up_questions": result.get("follow_up_questions", []),
        "processing_time_ms": result["processing_time_ms"],
    }


@kb_router.post("/{kb_id}/qa/feedback")
async def submit_qa_feedback(
    kb_id: UUID,
    data: QAFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Submete feedback para uma interacao Q&A."""
    repo = KnowledgeBaseRepository(db)

    interaction = repo.update_qa_interaction_feedback(
        interaction_id=data.interaction_id,
        is_helpful=data.is_helpful,
        rating=data.rating,
        feedback_text=data.feedback_text,
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )

    return {"success": True}


# =============================================================================
# AI Generation Endpoints
# =============================================================================


@kb_router.post("/{kb_id}/generate/article-structure")
async def generate_article_structure(
    kb_id: UUID,
    topic: str,
    article_type: str = "guide",
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Gera estrutura de artigo com IA."""
    generator = ArticleGenerator()

    result = generator.generate_article_structure(
        topic=topic,
        article_type=article_type,
    )

    return result


@kb_router.post("/{kb_id}/generate/summary")
async def generate_summary(
    kb_id: UUID,
    content: str,
    max_length: int = 200,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Gera resumo de conteudo."""
    generator = ArticleGenerator()

    result = generator.generate_summary(
        content=content,
        max_length=max_length,
    )

    return result


@kb_router.post("/{kb_id}/generate/faqs")
async def generate_faqs_from_content(
    kb_id: UUID,
    content: str,
    max_faqs: int = 5,
    topic: str | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Gera FAQs a partir de conteudo."""
    generator = ArticleGenerator()

    result = generator.generate_faq_from_content(
        content=content,
        max_faqs=max_faqs,
        topic=topic,
    )

    return result


@kb_router.post("/{kb_id}/generate/keywords")
async def extract_keywords(
    kb_id: UUID,
    content: str,
    max_keywords: int = 10,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Extrai keywords de conteudo."""
    generator = ArticleGenerator()

    keywords = generator.generate_keywords(
        content=content,
        max_keywords=max_keywords,
    )

    return {"keywords": keywords}


# =============================================================================
# Dashboard Endpoint
# =============================================================================


@kb_router.get("/dashboard/stats", response_model=KnowledgeBaseDashboard)
async def get_dashboard_stats(
    knowledge_base_id: UUID | None = None,
    condominio_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna estatisticas do dashboard."""
    repo = KnowledgeBaseRepository(db)

    stats = repo.get_dashboard_stats(
        knowledge_base_id=knowledge_base_id,
        condominio_id=condominio_id,
    )

    return stats
