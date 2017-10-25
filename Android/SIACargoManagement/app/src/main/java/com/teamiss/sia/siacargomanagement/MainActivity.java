package com.teamiss.sia.siacargomanagement;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import com.wonderkiln.camerakit.CameraListener;
import com.wonderkiln.camerakit.CameraView;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    CameraView camera;
    Button capture,reCapture;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        camera = findViewById(R.id.camera);
        capture = findViewById(R.id.button1);
        reCapture = findViewById(R.id.button2);

        camera.setCameraListener(new CameraListener() {
            @Override
            public void onPictureTaken(byte[] picture) {
                super.onPictureTaken(picture);

                // Create a bitmap
                Bitmap result = BitmapFactory.decodeByteArray(picture, 0, picture.length);
                camera.stop();
                //imageView.setVisibility(View.VISIBLE);
                //imageView.setImageBitmap(result);
            }
        });

        capture.setOnClickListener(this);
        reCapture.setOnClickListener(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        camera.start();
    }

    @Override
    protected void onPause() {
        camera.stop();
        super.onPause();
    }

    @Override
    public void onClick(View view) {
        if(view == capture)
            camera.captureImage();
        else if(view == reCapture)
            camera.start();
    }
}
