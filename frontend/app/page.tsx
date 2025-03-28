import { cookies } from "next/headers";

import { Mail } from "@/components/mail/Mail";
import { accounts, mails } from "@/public/TestMailData";
import Header from "@/components/Header";

export default async function Home() {
  const cookieStore = await cookies();
  const layout = cookieStore.get("react-resizable-panels:layout:mail");
  const collapsed = cookieStore.get("react-resizable-panels:collapsed");

  const defaultLayout = layout ? JSON.parse(layout.value) : undefined;
  const defaultCollapsed = collapsed ? JSON.parse(collapsed.value) : undefined;

  return (
    <main className="min-h-screen w-full">
      <>
        <div>
          <Header />
        </div>
        <div className="hidden flex-col md:flex">
          <Mail
            accounts={accounts}
            mails={mails}
            defaultLayout={defaultLayout}
            defaultCollapsed={defaultCollapsed}
            navCollapsedSize={4}
          />
        </div>
      </>
    </main>
  );
}
