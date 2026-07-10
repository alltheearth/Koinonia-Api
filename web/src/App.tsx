import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./lib/theme";
import { ContatosProvider } from "./lib/store";
import { Dashboard } from "./pages/Dashboard";
import { Contacts } from "./pages/Contacts";
import { HistoryPage } from "./pages/HistoryPage";
import { Assistant } from "./pages/Assistant";

function App() {
  return (
    <ThemeProvider>
      <ContatosProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contatos" element={<Contacts />} />
            <Route path="/historico" element={<HistoryPage />} />
            <Route path="/assistente" element={<Assistant />} />
          </Routes>
        </BrowserRouter>
      </ContatosProvider>
    </ThemeProvider>
  );
}

export default App;
