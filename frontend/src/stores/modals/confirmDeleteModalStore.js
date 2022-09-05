import {makeAutoObservable} from "mobx"
import logMessages from '../../log'


class ConfirmDeleteModalStore {
  show = false
  text = ''
  onYes = null
  onNo = null

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан ConfirmDeleteModalStore")
  }

  open(text, onYes, onNo) {
    logMessages('open ConfirmDeleteModal')
    this.text = text
    this.onYes = () => {
      onYes()
      this.close()
    }
    this.onNo = () => {
      onNo()
      this.close()
    }
    this.show = true
  }

  close() {
    logMessages('close ConfirmDeleteModal')
    this.show = false
    setTimeout(() => {
      this.text = ''
      this.onYes = null
      this.onNo = null
    }, 400)
  }

  setShow(bool) {
    this.show = bool
  }
}

export default new ConfirmDeleteModalStore()
