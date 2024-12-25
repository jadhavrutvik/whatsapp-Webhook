import httpx



class WhatsappSevice():
    BASE_URL="https://graph.facebook.com/v14.0/551602171364742/messages"
    ACCESS_TOKEN="EAAPp0EdFjMYBO39khNbSmjnbni7acmBuDdodj1PvaOs9NFZCBifBO6WQKhOJSAqx46H9Aw5uL2MJiL7xxMja0gfvrFMkHDSqF8eiZBBije30SBkwDkowepHIMMphsoZBlGYc2p6MgN9YDY2AvYQfDqChdQDSZC2dxiwisDceoLm27hdWGCaQ2pPOz9TCvoR2pvoAAZB5WNjjF7WtQCGUDiUiz4woZD"

    def __init__(self):
        self.headers={
            "Authorization":f"Bearer {self.ACCESS_TOKEN}",
            "Content-Type":"application/json"
        }
    async def send_message(self,mobile_no,message):
        try:
            payload={
                "messaging_product":"whatsapp",
                "to":mobile_no,
                "text":{"body":message}
            }

            with httpx.AsyncClient() as client:
                response=client.post(self.BASE_URL,json=payload,headers=self.headers)
            if response.status_code==200:
                return True , response.json()
            
            else:
                return False,response.json()
        except Exception as e:
            return False, {"error":str(e)}




