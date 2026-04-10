import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from './api'

function useAuth() {
  const [user, setUser] = useState(null)
  useEffect(() => {
    const token = localStorage.getItem('access')
    if (token) {
      api.get('/auth/me/').then(r => setUser(r.data)).catch(() => {
        localStorage.removeItem('access'); localStorage.removeItem('refresh')
      })
    }
  }, [])
  return { user, setUser }
}

function Login({ setUser }) {
  const nav = useNavigate()
  const [form, setForm] = useState({ email: 'admin@agora.local', password: '123456' })
  const [error, setError] = useState('')
  const submit = async (e) => {
    e.preventDefault()
    try {
      const { data } = await api.post('/auth/login/', form)
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      setUser(data.user)
      nav('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Falha no login')
    }
  }
  return <div className="container"><div className="card"><h2>Login</h2><form onSubmit={submit}>
    <input placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} />
    <input placeholder="Senha" type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} />
    <button>Entrar</button>
    {error && <p>{error}</p>}
  </form></div></div>
}

function Register() {
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({ name:'', email:'', password:'', cpf:'', phone:'' })
  const submit = async (e) => {
    e.preventDefault()
    await api.post('/auth/register/', form)
    setMsg('Cadastro realizado. Agora faça login.')
    setForm({ name:'', email:'', password:'', cpf:'', phone:'' })
  }
  return <div className="container"><div className="card"><h2>Cadastro</h2><form onSubmit={submit}>
    <input placeholder="Nome" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} />
    <input placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} />
    <input placeholder="Senha" type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} />
    <input placeholder="CPF" value={form.cpf} onChange={e=>setForm({...form,cpf:e.target.value})} />
    <input placeholder="Telefone" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})} />
    <button>Cadastrar</button>
    {msg && <p>{msg}</p>}
  </form></div></div>
}

function Private({ user, children }) { return user ? children : <Navigate to="/login" /> }

function Dashboard({ user }) {
  const [data, setData] = useState(null)
  useEffect(() => { if (user?.role === 'ADMIN') api.get('/dashboard/admin/').then(r=>setData(r.data)) }, [user])
  return <div className="container"><h2>Painel</h2>
    <div className="card"><p><strong>Usuário:</strong> {user?.name} ({user?.role})</p></div>
    {user?.role === 'ADMIN' && data && <div className="grid">
      <div className="card"><h3>Usuários</h3><p>{data.total_users}</p></div>
      <div className="card"><h3>Demandas</h3><p>{data.total_demands}</p></div>
      <div className="card"><h3>Abertas</h3><p>{data.open_demands}</p></div>
      <div className="card"><h3>Concluídas</h3><p>{data.closed_demands}</p></div>
    </div>}
  </div>
}

function Departments() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ name:'', description:'' })
  const load = ()=> api.get('/departments/').then(r=>setItems(r.data.results || r.data))
  useEffect(load, [])
  const submit = async (e)=>{ e.preventDefault(); await api.post('/departments/', form); setForm({name:'',description:''}); load() }
  return <div className="container"><div className="card"><h2>Departamentos</h2><form onSubmit={submit}><input placeholder="Nome" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/><textarea placeholder="Descrição" value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/><button>Salvar</button></form></div>
  <div className="card"><table className="table"><thead><tr><th>ID</th><th>Nome</th><th>Descrição</th></tr></thead><tbody>{items.map(i=><tr key={i.id}><td>{i.id}</td><td>{i.name}</td><td>{i.description}</td></tr>)}</tbody></table></div></div>
}

function Demands({ user }) {
  const [items, setItems] = useState([])
  const [departments, setDepartments] = useState([])
  const [form, setForm] = useState({ title:'', description:'', department:null, priority:'MEDIA', address:'', district:'' })
  const load = ()=> api.get('/demands/').then(r=>setItems(r.data.results || r.data))
  useEffect(()=>{ load(); api.get('/departments/').then(r=>setDepartments(r.data.results || r.data)).catch(()=>{}) }, [])
  const submit = async (e)=>{
    e.preventDefault()
    const payload = { ...form, citizen: user.id }
    await api.post('/demands/', payload)
    setForm({ title:'', description:'', department:null, priority:'MEDIA', address:'', district:'' })
    load()
  }
  return <div className="container"><div className="card"><h2>Demandas</h2><form onSubmit={submit}>
    <input placeholder="Título" value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/>
    <textarea placeholder="Descrição" value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/>
    <select value={form.department || ''} onChange={e=>setForm({...form,department:e.target.value || null})}><option value="">Selecione o departamento</option>{departments.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select>
    <select value={form.priority} onChange={e=>setForm({...form,priority:e.target.value})}><option>BAIXA</option><option>MEDIA</option><option>ALTA</option><option>URGENTE</option></select>
    <input placeholder="Endereço" value={form.address} onChange={e=>setForm({...form,address:e.target.value})}/>
    <input placeholder="Bairro" value={form.district} onChange={e=>setForm({...form,district:e.target.value})}/>
    <button>Abrir demanda</button>
  </form></div>
  <div className="card"><table className="table"><thead><tr><th>Protocolo</th><th>Título</th><th>Status</th><th>Prioridade</th></tr></thead><tbody>{items.map(i=><tr key={i.id}><td>{i.protocol}</td><td>{i.title}</td><td>{i.status}</td><td>{i.priority}</td></tr>)}</tbody></table></div></div>
}

function Users() {
  const [items, setItems] = useState([])
  const load = ()=> api.get('/users/').then(r=>setItems(r.data.results || r.data))
  useEffect(load, [])
  return <div className="container"><div className="card"><h2>Usuários</h2><table className="table"><thead><tr><th>ID</th><th>Nome</th><th>Email</th><th>Role</th></tr></thead><tbody>{items.map(i=><tr key={i.id}><td>{i.id}</td><td>{i.name}</td><td>{i.email}</td><td>{i.role}</td></tr>)}</tbody></table></div></div>
}

function Layout({ user, setUser }) {
  const nav = useNavigate()
  return <div className="container"><div className="nav">
    <Link to="/dashboard">Dashboard</Link>
    <Link to="/demands">Demandas</Link>
    {user?.role === 'ADMIN' && <><Link to="/departments">Departamentos</Link><Link to="/users">Usuários</Link></>}
    <button className="secondary" onClick={()=>{ localStorage.clear(); setUser(null); nav('/login') }}>Sair</button>
  </div></div>
}

export default function App() {
  const { user, setUser } = useAuth()
  return <>
    {user && <Layout user={user} setUser={setUser} />}
    <Routes>
      <Route path="/login" element={<Login setUser={setUser} />} />
      <Route path="/cadastro" element={<Register />} />
      <Route path="/dashboard" element={<Private user={user}><Dashboard user={user} /></Private>} />
      <Route path="/departments" element={<Private user={user}><Departments /></Private>} />
      <Route path="/demands" element={<Private user={user}><Demands user={user} /></Private>} />
      <Route path="/users" element={<Private user={user}><Users /></Private>} />
      <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} />} />
    </Routes>
  </>
}
