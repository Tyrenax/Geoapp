import '@fontsource/im-fell-english/400.css'
import '@fontsource/im-fell-english/400-italic.css'
import '@fontsource/alegreya/400.css'
import '@fontsource/alegreya/400-italic.css'
import '@fontsource/alegreya/500.css'
import '@fontsource/alegreya/700.css'
import '@fontsource/alegreya-sc/400.css'
import './app.css'
import { mount } from 'svelte'
import App from './App.svelte'

const app = mount(App, { target: document.getElementById('app')! })

export default app
