# AtomicHack

## 0. Create Docker env

``` bash
docker build -t welder:1.0 .
docker run -d -p 9090:80 --name welder_yolo welder:1.0 
```


## Train model and make a submission
1. Make sure you have a GPU machine, otherwise it will take more then eternity.
2. Put your files in the YOLO-friendly format (each image supported with the .txt file with bounding boxes, more [Here](https://blog.roboflow.com/how-to-train-yolov8-on-a-custom-dataset/)
3. Launch blocks in [HERE](train_model_simple.ipynb), this will produce the model.
4. Use the model in a Telegram bot (TBD) or make a submission via [THIS](make_submission.ipynb)
