package com.teamiss.sia.siacargomanagement;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.design.widget.TextInputLayout;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;

import butterknife.ButterKnife;
import butterknife.InjectView;


public class StartingActivity extends AppCompatActivity implements View.OnClickListener {

    private ProgressDialog progressDialog;
    @InjectView(R.id.input_num) EditText numCargo;
    @InjectView(R.id.btn_continue) Button next;
    @InjectView(R.id.cargo_num) TextInputLayout textInputLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_first_view);
        ButterKnife.inject(this);

        next.setOnClickListener(this);

        numCargo.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {}

            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {}

            @Override
            public void afterTextChanged(Editable s) {
                if(s.length() > 0)
                    textInputLayout.setErrorEnabled(false);
            }
        });

    }

    @Override
    public void onClick(View view) {
        if(view == next) {
            final String input = numCargo.getText().toString();
            if(input.isEmpty()){
                textInputLayout.setError("Please enter the number of cargo to be measured");
            }
            else {
                textInputLayout.setErrorEnabled(false);
                progressDialog = new ProgressDialog(this,
                        R.style.AppTheme_Dark_Dialog);
                progressDialog.setIndeterminate(true);
                progressDialog.setMessage("Lauching...");
                progressDialog.show();
                Runnable progressRunnable = new Runnable() {
                    @Override
                    public void run() {
                        progressDialog.cancel();
                        Intent nextView = new Intent(getApplicationContext(),MainActivity.class);
                        nextView.putExtra("numCargo",input);
                        startActivity(nextView);
                        finish();
                    }
                };

                Handler pdCanceller = new Handler();
                pdCanceller.postDelayed(progressRunnable, 1000);
            }
        }
    }
}
