import { cookies } from "next/headers";

import { Mail } from "@/components/mail/Mail";
import { accounts, mails } from "@/public/TestMailData";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Pacifico } from "next/font/google";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const pacifico = Pacifico({
  weight: "400",
  subsets: ["latin"],
});

export default async function Home() {
  const cookieStore = await cookies();
  const layout = cookieStore.get("react-resizable-panels:layout:mail");
  const collapsed = cookieStore.get("react-resizable-panels:collapsed");

  const defaultLayout = layout ? JSON.parse(layout.value) : undefined;
  const defaultCollapsed = collapsed ? JSON.parse(collapsed.value) : undefined;

  return (
    <main className="min-h-screen w-full">
      <>
        <div className="flex justify-center w-full">
          <Tabs defaultValue="mailbox" className="w-full">
            <div className="flex items-center justify-between w-full px-6">
              <div className={`${pacifico.className} text-6xl pb-5`}>avon</div>
              <div className="flex-1 flex justify-center">
                <TabsList className="grid w-6/12 grid-cols-2">
                  <TabsTrigger value="mailbox">Mailbox</TabsTrigger>
                  <TabsTrigger value="spreadsheet">Spreadsheet</TabsTrigger>
                </TabsList>
              </div>
              <Avatar>
                <AvatarImage
                  src="https://github.com/shadcn.png"
                  alt="@shadcn"
                />
                <AvatarFallback>CN</AvatarFallback>
              </Avatar>
            </div>
            <TabsContent value="mailbox">
              <div className="hidden flex-col md:flex">
                <Mail
                  accounts={accounts}
                  mails={mails}
                  defaultLayout={defaultLayout}
                  defaultCollapsed={defaultCollapsed}
                  navCollapsedSize={4}
                />
              </div>
            </TabsContent>
            <TabsContent value="spreadsheet"></TabsContent>
          </Tabs>
        </div>
      </>
    </main>
  );
}
