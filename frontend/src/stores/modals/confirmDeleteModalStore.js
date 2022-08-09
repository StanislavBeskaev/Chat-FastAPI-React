import {makeAutoObservable} from "mobx"


class ConfirmDeleteModalStore {
  show = false
  text = ''
  onYes = null
  onNo = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан ConfirmDeleteModalStore")
  }

  open(text, onYes, onNo) {
    console.log('open ConfirmDeleteModal')
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
    console.log('close ConfirmDeleteModal')
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
