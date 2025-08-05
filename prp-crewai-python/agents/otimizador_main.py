"""
Otimizador de Performance - Sistema PRP + CrewAI
Responsável por análise e otimização de campanhas em tempo real
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from a2a.server.apps import A2AStarletteApplication
from a2a.server.models import A2AAgent, A2ACommunication, A2ATask
from a2a.providers.a2a_api import APIRequest, APIResponse
import logging
import asyncio
import random

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OtimizadorAgent(A2AAgent):
    """Agente Otimizador de Performance"""
    
    def __init__(self):
        self.name = "Otimizador de Performance"
        self.id = "otimizador-performance"
        self.description = "Especialista em otimização de campanhas Meta Ads"
        self.capabilities = [
            "PERFORMANCE_ANALYSIS",
            "BUDGET_OPTIMIZATION", 
            "AUDIENCE_SEGMENTATION",
            "BID_STRATEGY",
            "CONVERSION_TRACKING",
            "CREATIVE_SCORING",
            "CAMPAIGN_AUTOMATION",
            "REPORT_GENERATION"
        ]
        self.current_campaigns = {}
    
    async def get_supported_tasks(self) -> List[str]:
        return [
            "analyze_performance",
            "optimize_budget",
            "segment_audiences",
            "adjust_bidding",
            "track_conversions",
            "score_creatives",
            "automate_rules",
            "generate_report"
        ]
    
    async def handle_message(self, message: str, context: Optional[Dict] = None) -> Dict:
        """Processa mensagens do orchestrator"""
        try:
            data = json.loads(message) if isinstance(message, str) else message
            task_type = data.get("task", "analyze_performance")
            
            logger.info(f"Processando task: {task_type}")
            
            if task_type == "analyze_performance":
                return await self.analyze_performance(data)
            elif task_type == "optimize_budget":
                return await self.optimize_budget(data)
            elif task_type == "segment_audiences":
                return await self.segment_audiences(data)
            elif task_type == "score_creatives":
                return await self.score_creatives(data)
            elif task_type == "generate_report":
                return await self.generate_report(data)
            else:
                return {"error": f"Task não suportada: {task_type}"}
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_performance(self, data: Dict) -> Dict:
        """Analisa performance das campanhas"""
        campaign_id = data.get("campaign_id", "campaign_001")
        
        # Simula análise de métricas
        metrics = {
            "impressions": random.randint(50000, 200000),
            "clicks": random.randint(1000, 10000),
            "conversions": random.randint(50, 500),
            "ctr": round(random.uniform(0.5, 5.0), 2),
            "cpc": round(random.uniform(0.50, 3.00), 2),
            "cpa": round(random.uniform(10.0, 50.0), 2),
            "roas": round(random.uniform(2.0, 8.0), 2),
            "frequency": round(random.uniform(1.2, 3.5), 2)
        }
        
        # Análise de tendências
        trends = {
            "ctr_trend": random.choice(["improving", "stable", "declining"]),
            "cpa_trend": random.choice(["improving", "stable", "declining"]),
            "audience_fatigue": metrics["frequency"] > 3.0,
            "budget_efficiency": metrics["roas"] > 3.0
        }
        
        # Recomendações baseadas na análise
        recommendations = []
        
        if trends["audience_fatigue"]:
            recommendations.append({
                "type": "audience_expansion",
                "priority": "high",
                "action": "Expandir audiência para reduzir frequência",
                "impact": "Redução de 20-30% no CPM"
            })
        
        if metrics["ctr"] < 1.0:
            recommendations.append({
                "type": "creative_refresh",
                "priority": "high", 
                "action": "Atualizar criativos para melhorar CTR",
                "impact": "Aumento de 50-80% no CTR"
            })
        
        if metrics["cpa"] > 30:
            recommendations.append({
                "type": "bidding_adjustment",
                "priority": "medium",
                "action": "Ajustar estratégia de lance para CPA objetivo",
                "impact": "Redução de 15-25% no CPA"
            })
        
        return {
            "analysis_id": f"analysis_{campaign_id}_{datetime.now().isoformat()}",
            "campaign_id": campaign_id,
            "metrics": metrics,
            "trends": trends,
            "recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def optimize_budget(self, data: Dict) -> Dict:
        """Otimiza distribuição de budget"""
        total_budget = data.get("budget", 10000)
        platforms = data.get("platforms", ["Facebook", "Instagram"])
        
        # Simula alocação otimizada
        allocation = {}
        remaining = total_budget
        
        for i, platform in enumerate(platforms):
            if i == len(platforms) - 1:
                allocation[platform] = remaining
            else:
                percentage = random.uniform(0.3, 0.6)
                amount = round(total_budget * percentage, 2)
                allocation[platform] = amount
                remaining -= amount
        
        # Alocação por objetivo
        objective_allocation = {
            "awareness": round(total_budget * 0.2, 2),
            "consideration": round(total_budget * 0.5, 2),
            "conversion": round(total_budget * 0.3, 2)
        }
        
        # Horários otimizados
        optimal_hours = {
            "morning": [7, 8, 9],
            "lunch": [12, 13],
            "evening": [18, 19, 20, 21],
            "late_night": [22, 23]
        }
        
        return {
            "optimization_id": f"opt_{datetime.now().timestamp()}",
            "total_budget": total_budget,
            "platform_allocation": allocation,
            "objective_allocation": objective_allocation,
            "optimal_schedule": optimal_hours,
            "expected_improvement": {
                "roas": "+25%",
                "cpa": "-18%",
                "conversions": "+35%"
            }
        }
    
    async def segment_audiences(self, data: Dict) -> Dict:
        """Segmenta audiências para melhor performance"""
        base_audience = data.get("target_audience", {})
        
        segments = [
            {
                "segment_id": "high_intent",
                "name": "Alta Intenção de Compra",
                "criteria": {
                    "behaviors": ["carrinho_abandonado", "visualizou_produto"],
                    "recency": "7_dias",
                    "frequency": "3+"
                },
                "size_estimate": random.randint(5000, 20000),
                "expected_cpa": round(random.uniform(15, 25), 2)
            },
            {
                "segment_id": "lookalike_buyers",
                "name": "Lookalike Compradores",
                "criteria": {
                    "source": "lista_compradores",
                    "similarity": "1-2%",
                    "exclusions": ["compradores_recentes"]
                },
                "size_estimate": random.randint(50000, 200000),
                "expected_cpa": round(random.uniform(25, 40), 2)
            },
            {
                "segment_id": "interest_based",
                "name": "Interesse + Comportamento",
                "criteria": {
                    "interests": base_audience.get("interests", []),
                    "behaviors": ["compras_online_frequente"],
                    "demographics": base_audience.get("demographics", {})
                },
                "size_estimate": random.randint(100000, 500000),
                "expected_cpa": round(random.uniform(35, 60), 2)
            }
        ]
        
        return {
            "segmentation_id": f"seg_{datetime.now().timestamp()}",
            "segments": segments,
            "total_reach": sum(s["size_estimate"] for s in segments),
            "recommended_budget_split": {
                "high_intent": "40%",
                "lookalike_buyers": "35%",
                "interest_based": "25%"
            }
        }
    
    async def score_creatives(self, data: Dict) -> Dict:
        """Pontua criativos baseado em performance"""
        creatives = data.get("creatives", [])
        
        scored_creatives = []
        for i, creative in enumerate(creatives):
            score = {
                "creative_id": creative.get("id", f"creative_{i}"),
                "overall_score": round(random.uniform(60, 95), 1),
                "metrics": {
                    "thumb_stop_rate": round(random.uniform(2, 8), 2),
                    "hook_strength": round(random.uniform(60, 95), 1),
                    "cta_clarity": round(random.uniform(70, 98), 1),
                    "brand_consistency": round(random.uniform(80, 100), 1)
                },
                "performance_prediction": {
                    "expected_ctr": round(random.uniform(1.5, 4.5), 2),
                    "expected_conversion_rate": round(random.uniform(2, 8), 2)
                },
                "recommendations": []
            }
            
            # Adiciona recomendações baseadas no score
            if score["metrics"]["thumb_stop_rate"] < 4:
                score["recommendations"].append(
                    "Melhorar primeiros 3 segundos para aumentar retenção"
                )
            
            if score["metrics"]["cta_clarity"] < 80:
                score["recommendations"].append(
                    "CTA precisa ser mais claro e direto"
                )
            
            scored_creatives.append(score)
        
        # Ordena por score
        scored_creatives.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return {
            "scoring_id": f"score_{datetime.now().timestamp()}",
            "creatives_analyzed": len(scored_creatives),
            "scores": scored_creatives,
            "top_performer": scored_creatives[0] if scored_creatives else None,
            "insights": {
                "best_performing_elements": [
                    "UGC style content",
                    "Problem-solution narrative",
                    "Social proof in first 5 seconds"
                ],
                "improvement_opportunities": [
                    "Testar diferentes hooks",
                    "Adicionar mais depoimentos",
                    "Criar variações com diferentes CTAs"
                ]
            }
        }
    
    async def generate_report(self, data: Dict) -> Dict:
        """Gera relatório completo de otimização"""
        campaign_id = data.get("campaign_id", "campaign_001")
        
        report = {
            "report_id": f"report_{campaign_id}_{datetime.now().strftime('%Y%m%d')}",
            "campaign_id": campaign_id,
            "period": {
                "start": "2024-01-01",
                "end": datetime.now().strftime("%Y-%m-%d")
            },
            "executive_summary": {
                "total_spend": round(random.uniform(8000, 12000), 2),
                "total_revenue": round(random.uniform(25000, 45000), 2),
                "overall_roas": round(random.uniform(2.5, 4.5), 2),
                "total_conversions": random.randint(400, 800)
            },
            "key_achievements": [
                "ROAS aumentou 35% após otimizações",
                "CPA reduzido em 22% com nova segmentação",
                "CTR melhorou 45% com novos criativos"
            ],
            "optimization_history": [
                {
                    "date": "2024-01-15",
                    "action": "Ajuste de público-alvo",
                    "result": "CPA -18%"
                },
                {
                    "date": "2024-01-20",
                    "action": "Novos criativos UGC",
                    "result": "CTR +45%"
                },
                {
                    "date": "2024-01-25",
                    "action": "Otimização de lances",
                    "result": "ROAS +25%"
                }
            ],
            "next_steps": [
                "Expandir para novos públicos lookalike",
                "Testar formatos de vídeo vertical",
                "Implementar campanhas de remarketing dinâmico"
            ]
        }
        
        return report

# Configuração da aplicação A2A
app = A2AStarletteApplication(port=8005)
agent = OtimizadorAgent()

# Configuração do agente para A2A
app.set_agent_info({
    "name": agent.name,
    "description": agent.description,
    "protocolVersion": "0.2.5",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False
    }
})

# Registra handlers
@app.on_task
async def handle_task(task: A2ATask) -> A2ATask:
    """Processa tasks recebidas"""
    logger.info(f"Recebendo task: {task.task_id}")
    
    try:
        result = await agent.handle_message(task.data, {"task_id": task.task_id})
        task.status = "completed"
        task.output = result
    except Exception as e:
        logger.error(f"Erro ao processar task: {str(e)}")
        task.status = "failed"
        task.output = {"error": str(e)}
    
    return task

@app.on_communication
async def handle_communication(comm: A2ACommunication) -> A2ACommunication:
    """Processa comunicações"""
    logger.info(f"Recebendo comunicação: {comm.message_id}")
    
    try:
        response = await agent.handle_message(comm.message)
        comm.response = json.dumps(response)
    except Exception as e:
        logger.error(f"Erro ao processar comunicação: {str(e)}")
        comm.response = json.dumps({"error": str(e)})
    
    return comm

# Endpoint customizado para health check
@app.app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": agent.name,
        "uptime": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Iniciando {agent.name} na porta 8005")
    uvicorn.run(app.app, host="0.0.0.0", port=8005)