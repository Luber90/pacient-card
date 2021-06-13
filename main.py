# Multi-frame tkinter application v2.3
import tkinter as tk
import asyncio
from fhirpy import AsyncFHIRClient

class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage, "", "")

    def switch_frame(self, frame_class, first, second):
        new_frame = frame_class(self, first, second)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()



class StartPage(tk.Frame):
    async def getCos(self):
        client = AsyncFHIRClient(
            'http://localhost:8080/baseR4',
            authorization='Bearer TOKEN',
        )
        if self.name!="":
            patients = client.resources('Patient').search(name=self.name)
        else:
            patients = client.resources('Patient')
        patients = await patients.fetch_all()
        a = 0
        for i in patients:
            self.pat.append([i.name[0].given[0] + " " + i.name[0].family, i.id])
            self.list.insert(a, i.name[0].given[0] + " " + i.name[0].family)
            a += 1
        self.list.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.list.yview)

    def onselect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        print('You selected item {}: "{}"'.format(index, value))
        self.master.switch_frame(PageOne, self.pat[index][1], "")

    def __init__(self, master, name, surname):
        self.name = name
        self.pat = []
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, text="surname").pack(side=tk.RIGHT)
        self.input = tk.Entry(self)
        self.input.pack(side=tk.RIGHT)
        self.list = tk.Listbox(self, width=40)
        self.list.bind('<<ListboxSelect>>', self.onselect)
        self.list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        tk.Button(self, text="Search",
                  command=lambda: master.switch_frame(StartPage, self.input.get(), "")).pack()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.getCos())


def dateToInt(s):
    i = s.find("T")
    return int(s[:i].replace("-", ""))

class PageOne(tk.Frame):

    async def getCos(self):
        client = AsyncFHIRClient(
            'http://localhost:8080/baseR4',
            authorization='Bearer TOKEN',
        )
        patients = client.resources('Patient').search(_id=self.id)
        patients = await patients.fetch()
        self.text.set("ID:{}   gender:{}   birth date:{}    name: {}".format(self.id, patients[0].gender, patients[0].birthDate, patients[0].name[0].given[0] + " " + patients[0].name[0].family))
        print(patients[0].gender, patients[0].birthDate, self.id, patients[0].name[0].given[0] + " " + patients[0].name[0].family)
        observations = await client.resources('Observation').search(subject=self.id).fetch_all()
        medical = await client.resources('MedicationRequest').search(subject=self.id).fetch_all()
        for i in observations:
            try:
                i.component
                self.all.append(
                    ["o", i.issued, i.code["coding"][0].display, str(i.component[0].valueQuantity.value),
                     i.component[0].valueQuantity.unit,
                     str(i.component[1].valueQuantity.value), i.component[1].valueQuantity.unit])
            except KeyError:
                try:
                    self.all.append(["o", i.issued, i.code["coding"][0].display, str(i.valueQuantity.value), i.valueQuantity.unit])
                except:
                    pass
        obs = 0
        for i in medical:
            try:
                self.all.append(["m", i.authoredOn, i.medicationCodeableConcept.coding[0].display])
                obs += 1
            except: pass
        self.all.sort(key=lambda x: dateToInt(x[1]))
        a = 0
        for i in self.all:
            if i[0] == "o":
                if(len(i)==5):
                    self.list.insert(a, i[1][:i[1].find("T")] + "  "+ i[2] + "  " + i[3]+" "+i[4])
                else:
                    self.list.insert(a, i[1][:i[1].find("T")] + "  " + i[2] + "  " + i[3] + " " + i[4] + "  " + i[5] + " " + i[6])
            else:
                self.list.insert(a, i[1][:i[1].find("T")]+" " + "Medication Request: " + i[2])
            a+=1
        self.list.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.list.yview)


    def __init__(self, master, id, _):
        self.id = id
        self.all = []
        tk.Frame.__init__(self, master)
        self.text = tk.StringVar()
        self.label = tk.Label(self, textvariable=self.text)
        self.label.pack(side=tk.TOP)
        self.list = tk.Listbox(self, width=150, height=50)
        self.list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.getCos())
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(StartPage, "", "")).pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()