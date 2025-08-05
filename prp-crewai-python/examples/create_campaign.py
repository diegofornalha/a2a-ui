"""
Exemplo de criação de campanha completa usando o sistema PRP + CrewAI
"""
import httpx
import asyncio
import json
from datetime import datetime
from typing import Dict, Any


class PRPCrewAIClient:
    """Cliente para interagir com o sistema PRP + CrewAI"""
    
    def __init__(self, orchestrator_url: str = "http://localhost:8001"):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova campanha"""
        response = await self.client.post(
            f"{self.orchestrator_url}/api/campaign/create",
            json=campaign_data
        )
        response.raise_for_status()
        return response.json()
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Obtém status de uma campanha"""
        response = await self.client.get(
            f"{self.orchestrator_url}/api/campaign/{campaign_id}/status"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_agents_status(self) -> Dict[str, Any]:
        """Obtém status de todos os agentes"""
        response = await self.client.get(
            f"{self.orchestrator_url}/api/agents/status"
        )
        response.raise_for_status()
        return response.json()
    
    async def wait_for_completion(self, campaign_id: str, max_wait: int = 300):
        """Aguarda conclusão da campanha (max_wait em segundos)"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < max_wait:
            status = await self.get_campaign_status(campaign_id)
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Campanha falhou: {status.get('error')}")
            
            print(f"Status: {status['status']} - {status.get('progress', 0)}% completo")
            await asyncio.sleep(5)
        
        raise TimeoutError(f"Timeout aguardando conclusão da campanha")
    
    async def close(self):
        """Fecha o cliente HTTP"""
        await self.client.aclose()


async def main():
    """Exemplo completo de criação de campanha"""
    
    # Inicializa cliente
    client = PRPCrewAIClient()
    
    try:
        # 1. Verifica status dos agentes
        print("🔍 Verificando status dos agentes...")
        agents_status = await client.get_agents_status()
        
        print("\n📊 Status dos Agentes:")
        for agent, status in agents_status.items():
            emoji = "✅" if status["status"] == "online" else "❌"
            print(f"  {emoji} {agent}: {status['status']}")
        
        # Verifica se todos os agentes estão online
        all_online = all(s["status"] == "online" for s in agents_status.values())
        if not all_online:
            print("\n⚠️  Nem todos os agentes estão online!")
            print("Execute ./start_all.sh para iniciar o sistema")
            return
        
        # 2. Define dados da campanha
        campaign_data = {
            "client_name": "Boutique Elegância Feminina",
            "business_type": "Loja de roupas femininas premium",
            "campaign_goal": "Aumentar vendas online em 50% e captar 1000 novos clientes",
            "target_audience": {
                "age_range": "25-45",
                "gender": "female",
                "interests": [
                    "moda feminina",
                    "roupas de grife",
                    "tendências de moda",
                    "estilo pessoal",
                    "compras online"
                ],
                "behaviors": [
                    "compras online frequentes",
                    "segue influencers de moda",
                    "interesse em marcas premium"
                ],
                "income_level": "média-alta e alta",
                "location": "Brasil - Grandes centros urbanos"
            },
            "budget": 15000.00,
            "currency": "BRL",
            "duration_days": 30,
            "platforms": ["Facebook", "Instagram"],
            "additional_info": {
                "unique_selling_points": [
                    "Peças exclusivas e limitadas",
                    "Atendimento personalizado via WhatsApp",
                    "Frete grátis acima de R$ 299",
                    "Programa de fidelidade com cashback"
                ],
                "main_competitors": [
                    "Zara",
                    "Renner",
                    "C&A Premium"
                ],
                "previous_campaigns": {
                    "last_ctr": 2.5,
                    "last_conversion_rate": 3.2,
                    "best_performing_creative": "vídeo UGC com cliente real"
                }
            }
        }
        
        # 3. Cria a campanha
        print("\n🚀 Criando campanha...")
        print(f"Cliente: {campaign_data['client_name']}")
        print(f"Objetivo: {campaign_data['campaign_goal']}")
        print(f"Orçamento: R$ {campaign_data['budget']:,.2f}")
        
        campaign = await client.create_campaign(campaign_data)
        campaign_id = campaign["campaign_id"]
        
        print(f"\n✅ Campanha criada: {campaign_id}")
        print(f"Status inicial: {campaign['status']}")
        
        # 4. Acompanha o progresso
        print("\n⏳ Aguardando processamento pelos agentes...")
        print("Isso pode levar alguns minutos...\n")
        
        result = await client.wait_for_completion(campaign_id)
        
        # 5. Exibe resultados
        print("\n🎉 Campanha concluída com sucesso!")
        print("\n📋 Resultados:")
        
        # Estratégia
        if "strategy" in result:
            print("\n📊 ESTRATÉGIA:")
            strategy = result["strategy"]
            print(f"  • Personas identificadas: {len(strategy.get('target_personas', []))}")
            print(f"  • KPIs definidos: {', '.join(strategy.get('kpis', {}).keys())}")
            print(f"  • Orçamento por plataforma:")
            for platform, budget in strategy.get('budget_allocation', {}).items():
                print(f"    - {platform}: R$ {budget:,.2f}")
        
        # Criativos
        if "creatives" in result:
            print("\n🎨 CRIATIVOS:")
            creatives = result["creatives"]
            print(f"  • Variações criadas: {len(creatives.get('variations', []))}")
            print(f"  • Formatos: {', '.join(set(v.get('format', '') for v in creatives.get('variations', [])))}")
            print(f"  • Paleta de cores: {', '.join(creatives.get('color_palette', []))}")
        
        # Copy
        if "copy" in result:
            print("\n✍️ COPY:")
            copy = result["copy"]
            print(f"  • Headlines criadas: {len(copy.get('headlines', []))}")
            print(f"  • CTAs testados: {len(copy.get('cta_options', []))}")
            print(f"  • Gatilhos mentais: {', '.join(copy.get('mental_triggers', []))}")
            
            # Mostra algumas headlines
            if copy.get('headlines'):
                print("\n  Exemplos de Headlines:")
                for i, headline in enumerate(copy['headlines'][:3], 1):
                    print(f"    {i}. {headline}")
        
        # Otimizações
        if "optimizations" in result:
            print("\n⚡ OTIMIZAÇÕES:")
            opt = result["optimizations"]
            print(f"  • Segmentos de audiência: {len(opt.get('audience_segments', []))}")
            print(f"  • Melhorias esperadas:")
            for metric, improvement in opt.get('expected_improvements', {}).items():
                print(f"    - {metric}: {improvement}")
        
        # Salva resultado completo
        output_file = f"campaign_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultado completo salvo em: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    print("🎭 PRP + CrewAI - Exemplo de Criação de Campanha")
    print("=" * 50)
    asyncio.run(main())