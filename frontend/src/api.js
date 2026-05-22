import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getPosts = (params) =>
  api.get('/posts', { params }).then((r) => r.data)

export const getPost = (id) =>
  api.get(`/posts/${id}`).then((r) => r.data)

export const getPostCategories = () =>
  api.get('/posts/categories').then((r) => r.data)

export const getSources = () =>
  api.get('/sources').then((r) => r.data)

export const syncNow = () => api.post('/sync').then((r) => r.data)
