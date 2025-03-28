import React from "react";
import { Pacifico } from "next/font/google";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
const pacifico = Pacifico({
  weight: "400",
  subsets: ["latin"],
});

const Header = () => {
  return (
    <div className="flex items-center">
      <div className={`${pacifico.className} text-6xl px-4 pb-5`}>avon</div>
      <div className="flex justify-center w-full">
        <Tabs defaultValue="mailbox" className="w-[400px]">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="mailbox">Mailbox</TabsTrigger>
            <TabsTrigger value="spreadsheet">Spreadsheet</TabsTrigger>
          </TabsList>
          <TabsContent value="mailbox"></TabsContent>
          <TabsContent value="spreadsheet"></TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Header;
