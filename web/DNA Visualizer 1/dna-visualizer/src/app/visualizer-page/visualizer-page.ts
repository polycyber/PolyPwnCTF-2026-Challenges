import { Component, signal, Signal, WritableSignal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormsModule, Form, FormGroup } from '@angular/forms';
import { catchError, firstValueFrom, of } from 'rxjs';

@Component({
  selector: 'app-visualizer-page',
  imports: [ReactiveFormsModule, FormsModule],
  templateUrl: './visualizer-page.html',
  styleUrl: './visualizer-page.css',
})
export class VisualizerPage {

  generateForm: FormGroup;
  submissionSuccess: WritableSignal<boolean> = signal(false);
  submissionStatus: WritableSignal<string> = signal('');
  moleculeResults: WritableSignal<string> = signal('');
  

    constructor(private http: HttpClient, private formBuilder: FormBuilder) {
      this.generateForm = this.formBuilder.group({
      sequence: '',
    });
  }

    async generate() {
    this.submissionSuccess.set(false);
    console.log("Sequence submitting: ", this.generateForm.value);
    if (!this.generateForm.value.sequence) {
      this.submissionStatus.set('Sequence is required.');
      return;
    }

    if (!/^[ACGT\.]+$/.test(this.generateForm.value.sequence)) {
      this.submissionStatus.set('Invalid Nucleotide given.');
      return;
    }

    // (mode: string, sequenceLength: number) {
    // Handle profile submission logic here
    // Send a POST request to the server with the profile data from the form in the HTML
      
        // const hostname = process.env.API_HOSTNAME; // Assuming you have set this in your environment
        // const hostname = "http://127.0.0.1";
        // const port = 3500;
        try {
          // const result = await firstValueFrom(this.http.get(`${hostname}/`).pipe(catchError((error) => {return of(undefined)})));
          const headers = new HttpHeaders({ 'Content-Type': 'application/json'});
          const result = await firstValueFrom(this.http.post(`api/generate/`, 
            { sequence: this.generateForm.value.sequence }, { headers }).pipe(catchError((error) => {return of(undefined)}))
          );
          
          if (!result) {
            console.error("Error submitting sequence");
            this.submissionSuccess.set(false);
            this.submissionStatus.set('Error submitting sequence.');
            return;
          }
          console.log("Sequence submission result: ", result);
          this.submissionSuccess.set(true);
          this.submissionStatus.set('Sequence submitted successfully!');

          const renderRes = (result as any)?.molecule
          this.moleculeResults.set(renderRes);//.replaceAll('\n', '<br>'));

        } catch (error) {
          console.error("Error submitting sequence: ", error);
          this.submissionSuccess.set(false);
          this.submissionStatus.set('Error submitting sequence.');
        }
      }



}
